"""Sitemap related data"""
from django.urls import reverse

from core.sitemap import SailtrailSitemap


class LeaderboardSitemap(SailtrailSitemap):
    """Sitemap settings for leaderboard entry"""
    changefreq = "daily"

    def items(self) -> list:
        """Get items to appear in this sitemap section"""
        return ['leaderboards']

    def location(self, obj) -> str:
        """Get location for these entries"""
        return reverse(obj)
