from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^upload$', 'activities.views.upload', name='upload'),
    url(r'(\d+)/delete$', 'activities.views.delete', name='delete_activity'),
    url(r'(\d+)/trim$', 'activities.views.trim', name='trim_activity'),
    url(r'(\d+)/untrim$', 'activities.views.untrim', name='untrim_activity'),
    url(r'(\d+)/details/$', 'activities.views.details', name='details'),
    url(r'(\d+)/$', 'activities.views.view', name='view_activity'),
)
