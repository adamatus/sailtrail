"""Sitemap related data"""
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.urls import reverse

from api.helper import get_active_users
from core.sitemap import SailtrailSitemap


class UsersSitemap(SailtrailSitemap):
    """Sitemap settings for user entries"""
    changefreq = "weekly"

    def items(self) -> QuerySet:
        """Get items to appear in this sitemap section"""
        return get_active_users()

    def location(self, user: User) -> str:
        """Get location for these entries"""
        return reverse('users:user', args=[str(user.username)])
