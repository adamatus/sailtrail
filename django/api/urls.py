"""Routing for activity related pages"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from api import views


app_name = 'api'  # pylint: disable=invalid-name

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

    url(r'activity/(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/json$',
        views.TrackJSONView.as_view(),
        name="track_json"),
    url(r'activity/(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/full_json$',
        views.FullTrackJSONView.as_view(),
        name="full_track_json"),

    url(r'activity/(?P<pk>\d+)/delete$',
        login_required(views.DeleteActivityView.as_view()),
        name='delete_activity'),

    url(r'activity/(?P<pk>\d+)/json$',
        views.ActivityJSONView.as_view(),
        name='activity_json'),


    url(r'activities/(?P<pk>\d+)/wind_direction$',
        login_required(views.WindDirection.as_view()),
        name='activity_wind_direction'),
]
