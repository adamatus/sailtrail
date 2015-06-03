from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from activities import views as activity_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', activity_views.home_page, name='home'),
    url(r'^activities/', include('activities.urls')),
    url('^register/$', activity_views.register, name='register'),
    url(r'^about', TemplateView.as_view(
        template_name='about.html'),
        name='about'),

    url(r'^users/$', activity_views.user_list, name='user_list'),
    url(r'^users/(?P<username>\w+)/$', activity_views.user_page, name='user'),

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$',
        auth_views.logout,
        {'next_page': '/'}, name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
]
