"""Sitemap related data"""
from django.core.urlresolvers import reverse

from core.sitemap import SailtrailSitemap


class LeaderboardSitemap(SailtrailSitemap):
    """Sitemap settings for leaderboard entry"""
    changefreq = "daily"

    def items(self):
        """Get items to appear in this sitemap section"""
        return ['leaderboards']

    def location(self, item):
        """Get location for these entries"""
        return reverse(item)
