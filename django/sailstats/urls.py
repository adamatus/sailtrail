from django.conf.urls import patterns, include, url
from django.contrib import admin

from activities import views as activity_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', activity_views.home_page, name='home'),
    url(r'^activities/', include('activities.urls')),
    url('^register/$', activity_views.register, name='register'),

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$',
        auth_views.logout,
        {'next_page': '/'}, name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
]
