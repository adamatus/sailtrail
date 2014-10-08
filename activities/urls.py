from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^upload$', 'activities.views.upload', name='upload'),
    url(r'(\d+)/delete$', 'activities.views.delete', name='delete_activity'),
    url(r'(\d+)/$', 'activities.views.view', name='view_activity'),
)
