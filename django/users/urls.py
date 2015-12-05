"""Routing for activity related pages"""
from django.conf.urls import url

from .views import UserView, UserListView

urlpatterns = [
    url(r'^$', UserListView.as_view(), name='user_list'),
    url(r'^(?P<slug>\w+)/$', UserView.as_view(), name='user'),
]
