from django.conf.urls import patterns, url

from djangojs.views import JasmineView

urlpatterns = patterns(
    '',
    url(r'^upload$', 'activities.views.upload', name='upload'),
    url(r'(\d+)/delete$', 'activities.views.delete', name='delete_activity'),
    url(r'(\d+)/details/$', 'activities.views.details', name='details'),
    url(r'(\d+)/$', 'activities.views.view', name='view_activity'),
    url(r'^jasmine/track_viewer$', 
        JasmineView.as_view(template_name='tests/track_viewer.html'),
        name='jasmine'),
    url(r'^jasmine/speed_viewer$', 
        JasmineView.as_view(template_name='tests/speed_viewer.html'),
        name='jasmine'),
)
