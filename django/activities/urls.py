"""Routing for activity related pages"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from activities import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='activity_list'),
    url(r'^upload$', login_required(views.UploadView.as_view()),
        name='upload'),

    url(r'(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/$',
        views.ActivityTrackView.as_view(),
        name="view_track"),
    url(r'(?P<activity_id>\d+)/tracks/upload$',
        views.UploadTrackView.as_view(),
        name='upload_track'),

    url(r'(?P<pk>\d+)/details/$', login_required(views.DetailsView.as_view()),
        name='details'),
    url(r'(?P<pk>\d+)/$', views.ActivityView.as_view(), name='view_activity'),
]
