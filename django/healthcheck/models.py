"""Simple model to hold healthcheck results"""
from django.db import models


class Healthcheck(models.Model):
    """Small table used to record healthcheck calls"""
    source = models.CharField(max_length=32, null=False)
    created = models.DateTimeField(auto_now_add=True)
