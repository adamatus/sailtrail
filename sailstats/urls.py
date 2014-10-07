from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^$', 'activities.views.home_page', name='home'),
    url(r'^activities/', include('activities.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
