from django.db import models


class Activity(models.Model):
    filename = models.TextField(null=False, blank=False)
    filepath = models.TextField(null=True, blank=True)
    
