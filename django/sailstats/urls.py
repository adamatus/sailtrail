from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^$', 'activities.views.home_page', name='home'),
    url(r'^activities/', include('activities.urls')),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),
    url('^register/$', 'activities.views.register', name='register'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
)
