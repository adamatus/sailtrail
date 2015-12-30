"""Sitemap related data"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import QuerySet

from core.sitemap import SailtrailSitemap


class UsersSitemap(SailtrailSitemap):
    """Sitemap settings for user entries"""
    changefreq = "weekly"

    def items(self) -> QuerySet:
        """Get items to appear in this sitemap section"""
        return User.objects.filter(is_active=True, is_superuser=False)

    def location(self, user: User) -> str:
        """Get location for these entries"""
        return reverse('user', args=[str(user.username)])
