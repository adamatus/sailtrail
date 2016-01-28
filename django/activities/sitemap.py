"""Sitemap related data"""
from django.db.models import QuerySet

from api.helper import get_public_activities
from api.models import Activity
from core.sitemap import SailtrailSitemap


class ActivitySitemap(SailtrailSitemap):
    """Sitemap settings for activity entries"""
    changefreq = "weekly"

    def items(self) -> QuerySet:
        """Get items to appear in this sitemap section"""
        return get_public_activities()

    @staticmethod
    def lastmod(activity: Activity) -> Activity:
        """Get last modified date for these entries"""
        return activity.modified
