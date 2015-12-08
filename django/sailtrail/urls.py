from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from activities.sitemap import ActivitySitemap, LeaderboardSitemap, \
    UsersSitemap
from activities.views import HomePageView

sitemaps = {'activities': ActivitySitemap,
            'leaderboards': LeaderboardSitemap,
            'users': UsersSitemap,
            }

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),

    url(r'^activities/', include('activities.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^leaderboards/', include('leaders.urls')),
    url(r'^users/', include('users.urls')),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^about', TemplateView.as_view(
        template_name='about.html'),
        name='about'),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'^robots\.txt$', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'),
        name='robots.txt',
        ),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
]
