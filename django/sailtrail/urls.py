from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView

from activities import views as activity_views
from activities.sitemap import ActivitySitemap, LeaderboardSitemap, \
    UsersSitemap

sitemaps = {'activities': ActivitySitemap,
            'leaderboards': LeaderboardSitemap,
            'users': UsersSitemap,
            }

urlpatterns = [
    url(r'^$', activity_views.home_page, name='home'),
    url(r'^activities/', include('activities.urls')),
    url(r'^about', TemplateView.as_view(
        template_name='about.html'),
        name='about'),

    url(r'^users/$', activity_views.user_list, name='user_list'),
    url(r'^users/(?P<username>\w+)/$', activity_views.user_page, name='user'),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
]
