"""Routing for activity related pages"""
from django.conf.urls import url

from activities import views

urlpatterns = [
    url(r'^$', views.activity_list, name='activity_list'),
    url(r'^leaderboards$', views.leaderboards, name='leaderboards'),
    url(r'^upload$', views.upload, name='upload'),

    url(r'(\d+)/tracks/(\d+)/$', views.view_track, name="view_track"),
    url(r'(\d+)/tracks/upload$', views.upload_track, name='upload_track'),

    url(r'(\d+)/details/$', views.details, name='details'),
    url(r'(\d+)/$', views.view, name='view_activity'),
]
