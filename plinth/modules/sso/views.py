#
# This file is part of Plinth.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Views for the Single Sign On module of Plinth
"""

import os
import urllib
import logging

from .forms import AuthenticationForm

from plinth import actions

from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView

from django.shortcuts import render_to_response

from axes.utils import reset

PRIVATE_KEY_FILE_NAME = 'privkey.pem'
SSO_COOKIE_NAME = 'auth_pubtkt'
KEYS_DIRECTORY = '/etc/apache2/auth-pubtkt-keys'

logger = logging.getLogger(__name__)


def set_ticket_cookie(user, response):
    """Generate and set a mod_auth_pubtkt as a cookie in the provided
    response.
    """
    tokens = list(map(lambda g: g.name, user.groups.all()))
    private_key_file = os.path.join(KEYS_DIRECTORY, PRIVATE_KEY_FILE_NAME)
    ticket = actions.superuser_run('auth-pubtkt', [
        'generate-ticket', '--uid', user.username, '--private-key-file',
        private_key_file, '--tokens', ','.join(tokens)
    ])
    response.set_cookie(SSO_COOKIE_NAME, urllib.parse.quote(ticket))
    return response


class SSOLoginView(LoginView):
    """View to login to Plinth and set a auth_pubtkt cookie which will be
    used to provide Single Sign On for some other applications
    """
    redirect_authenticated_user = True
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        response = super(SSOLoginView, self).dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            return set_ticket_cookie(request.user, response)
        else:
            return response


class CaptchaLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login.html'
    form_class = AuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        response = super(CaptchaLoginView, self).dispatch(
            request, *args, **kwargs)
        if request.POST:
            if request.user.is_authenticated:
                ip = get_ip_address_from_request(request)
                reset(ip=ip)
                return set_ticket_cookie(request.user, response)
            else:
                return response
        return response


def get_ip_address_from_request(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    logger.warning("IP address is " + ip)
    return ip


class SSOLogoutView(LogoutView):
    """View to log out of Plinth and remove the auth_pubtkt cookie"""
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        response = super(SSOLogoutView, self).dispatch(request, *args,
                                                       **kwargs)
        response.delete_cookie(SSO_COOKIE_NAME)
        return response


@login_required
def refresh(request):
    """Simulate cookie refresh - redirect logged in user with a new cookie"""
    redirect_url = request.GET.get(REDIRECT_FIELD_NAME, '')
    response = HttpResponseRedirect(redirect_url)
    response.delete_cookie(SSO_COOKIE_NAME)
    return set_ticket_cookie(request.user, response)
