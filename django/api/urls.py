"""Routing for activity related pages"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from api import views

urlpatterns = [
    url(r'activity/(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/delete$',
        login_required(views.DeleteTrackView.as_view()),
        name='delete_track'),
    url(r'activity/(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/trim$',
        login_required(views.TrimView.as_view()),
        name='trim_track'),
    url(r'activity/(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/untrim$',
        login_required(views.UntrimView.as_view()),
        name='untrim_track'),

    url(r'activity/(\d+)/tracks/(\d+)/json$', views.track_json,
        name="track_json"),

    url(r'activity/(?P<pk>\d+)/delete$',
        login_required(views.DeleteActivityView.as_view()),
        name='delete_activity'),

    url(r'activity/(\d+)/json$', views.activity_json, name='activity_json'),
    url(r'activities/(?P<pk>\d+)/wind_direction$',
        login_required(views.WindDirection.as_view()),
        name='activity_wind_direction'),
]
