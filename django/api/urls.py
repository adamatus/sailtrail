"""Routing for activity related pages"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from api import views

urlpatterns = [
    url(r'activity/(\d+)/tracks/(\d+)/delete$', views.delete_track,
        name='delete_track'),
    url(r'activity/(\d+)/tracks/(\d+)/trim$', views.trim, name='trim_track'),
    url(r'activity/(\d+)/tracks/(\d+)/untrim$', views.untrim,
        name='untrim_track'),
    url(r'activity/(\d+)/tracks/(\d+)/json$', views.track_json,
        name="track_json"),
    url(r'activity/(\d+)/tracks/(\d+)/full_json$', views.full_track_json,
        name="full_track_json"),

    url(r'activity/(\d+)/delete$', views.delete, name='delete_activity'),
    url(r'activity/(\d+)/json$', views.activity_json, name='activity_json'),
    url(r'activities/(?P<pk>\d+)/wind_direction$',
        login_required(views.WindDirection.as_view()),
        name='activity_wind_direction'),
]
