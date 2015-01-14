from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^upload$', 'activities.views.upload', name='upload'),
    url(r'(\d+)/delete$', 'activities.views.delete', name='delete_activity'),
    url(r'(\d+)/tracks/(\d+)/delete$',
        'activities.views.delete_track',
        name='delete_track'),
    url(r'(\d+)/tracks/(\d+)/trim$',
        'activities.views.trim',
        name='trim_track'),
    url(r'(\d+)/tracks/(\d+)/untrim$',
        'activities.views.untrim',
        name='untrim_track'),
    url(r'(\d+)/details/$', 'activities.views.details', name='details'),
    url(r'(\d+)/tracks/(\d+)/$',
        'activities.views.view_track',
        name="view_track"),
    url(r'(\d+)/tracks/upload$',
        'activities.views.upload_track',
        name='upload_track'),
    url(r'(\d+)/$', 'activities.views.view', name='view_activity'),
)
