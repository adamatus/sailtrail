from django.conf.urls import patterns, url

from activities import views

urlpatterns = [
    url(r'^$', views.activity_list, name='activity_list'),
    url(r'^upload$', views.upload, name='upload'),

    url(r'(\d+)/tracks/(\d+)/delete$', views.delete_track, name='delete_track'),
    url(r'(\d+)/tracks/(\d+)/trim$', views.trim, name='trim_track'),
    url(r'(\d+)/tracks/(\d+)/untrim$', views.untrim, name='untrim_track'),
    url(r'(\d+)/tracks/(\d+)/$', views.view_track, name="view_track"),
    url(r'(\d+)/tracks/(\d+)/json$', views.track_json, name="track_json"),
    url(r'(\d+)/tracks/upload$', views.upload_track, name='upload_track'),

    url(r'^users/$', views.user_list, name='user_list'),
    url(r'^users/(?P<username>\w+)/$', views.user_page, name='user'),

    url(r'(\d+)/details/$', views.details, name='details'),
    url(r'(\d+)/delete$', views.delete, name='delete_activity'),
    url(r'(\d+)/json$', views.activity_json, name='activity_json'),
    url(r'(\d+)/$', views.view, name='view_activity'),
]
