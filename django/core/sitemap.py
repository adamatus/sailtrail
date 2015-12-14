"""Sitemap related data"""
from django.contrib.sitemaps import Sitemap


class SailtrailSitemap(Sitemap):
    """Base sitemap settings"""
    priority = 0.5
    protocol = 'https'
