"""Routing for activity related pages"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.user_list, name='user_list'),
    url(r'^(?P<username>\w+)/$', views.user_page, name='user'),
]
