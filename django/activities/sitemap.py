"""Sitemap related data"""
from api.models import Activity

from core.sitemap import SailtrailSitemap


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
