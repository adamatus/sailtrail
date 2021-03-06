"""Routing for activity related pages"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from activities import views
from homepage.views import HomePageView


app_name = "activities"  # pylint: disable=invalid-name

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='activity_list'),
    url(r'^upload$', login_required(views.UploadView.as_view()),
        name='upload'),

    url(r'(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/$',
        login_required(views.ActivityTrackView.as_view()),
        name="view_track"),
    url(r'(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/trim$',
        login_required(views.ActivityTrackTrimView.as_view()),
        name="edit_track_trim"),
    url(r'(?P<activity_id>\d+)/tracks/(?P<pk>\d+)/download$',
        login_required(views.ActivityTrackDownloadView.as_view()),
        name="download_track_file"),
    url(r'(?P<activity_id>\d+)/tracks/upload$',
        login_required(views.UploadTrackView.as_view()),
        name='upload_track'),

    url(r'(?P<pk>\d+)/details/$', login_required(views.DetailsView.as_view()),
        name='details'),
    url(r'(?P<pk>\d+)/$', views.ActivityView.as_view(), name='view_activity'),
]
