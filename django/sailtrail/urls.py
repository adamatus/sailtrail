from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView

from activities.sitemap import ActivitySitemap
from core.views import NotFoundView, PermissionDeniedView, BadRequestView, \
    InternalServerErrorView
from homepage.views import HomePageView
from leaders.sitemap import LeaderboardSitemap
from users.sitemap import UsersSitemap
from users.views import ChangePasswordView

sitemaps = {'activities': ActivitySitemap,
            'leaderboards': LeaderboardSitemap,
            'users': UsersSitemap,
            }

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),

    url(r'^activities/', include('activities.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^boats/', include('boats.urls')),
    url(r'^leaderboards/', include('leaders.urls')),
    url(r'^users/', include('users.urls')),

    url(r'^accounts/password/change',
        login_required(ChangePasswordView.as_view()),
        name='change_password'),
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

    url(r'^healthcheck/', include('healthcheck.urls')),

    url(r'^admin/', admin.site.urls),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = BadRequestView.as_error_view()
handler404 = NotFoundView.as_error_view()
handler403 = PermissionDeniedView.as_error_view()
handler500 = InternalServerErrorView.as_error_view()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
