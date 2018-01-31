"""Routing for user related pages"""
from django.conf.urls import url

from boats.views import UsersBoatsView
from .views import UserView, UserListView, UserSettingsView

app_name = 'users'  # pylint: disable=invalid-name

urlpatterns = [
    url(r'^$', UserListView.as_view(), name='user_list'),
    url(r'^(?P<username>\w+)/$', UserView.as_view(), name='user'),
    url(r'^(?P<slug>\w+)/settings$', UserSettingsView.as_view(),
        name='user_settings'),
    url(r'^(?P<username>\w+)/boats/$', UsersBoatsView.as_view(), name='boats'),
]
