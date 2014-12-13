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
URLs for the Users module
"""

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^sys/users/$', views.UserList.as_view(), name='index'),
    url(r'^sys/users/create/$', views.UserCreate.as_view(), name='create'),
    url(r'^sys/users/(?P<slug>[\w.@+-]+)/edit/$', views.UserUpdate.as_view(),
        name='edit'),
    url(r'^sys/users/(?P<slug>[\w.@+-]+)/delete/$', views.UserDelete.as_view(),
        name='delete'),
    url(r'^sys/users/(?P<slug>[\w.@+-]+)/change_password/$',
        views.UserChangePassword.as_view(), name='change_password'),
)
