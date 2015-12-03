"""Sitemap related data"""
from django.contrib.auth.models import User
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from api.models import Activity


class SailtrailSitemap(Sitemap):
    """Base sitemap settings"""
    priority = 0.5
    protocol = 'https'


class LeaderboardSitemap(SailtrailSitemap):
    """Sitemap settings for leaderboard entry"""
    changefreq = "daily"

    def items(self):
        """Get items to appear in this sitemap section"""
        return ['leaderboards']

    def location(self, item):
        """Get location for these entries"""
        return reverse(item)


class ActivitySitemap(SailtrailSitemap):
    """Sitemap settings for activity entries"""
    changefreq = "weekly"

    def items(self):
        """Get items to appear in this sitemap section"""
        return Activity.objects.filter(private=False)

    @staticmethod
    def lastmod(activity):
        """Get last modified date for these entries"""
        return activity.modified


class UsersSitemap(SailtrailSitemap):
    """Sitemap settings for user entries"""
    changefreq = "weekly"

    def items(self):
        """Get items to appear in this sitemap section"""
        return User.objects.filter(is_active=True, is_superuser=False)

    def location(self, obj):
        """Get location for these entries"""
        return reverse('user', args=[str(obj.username)])
