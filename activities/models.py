from django.db import models


class Activity(models.Model):
    upfile = models.FileField(upload_to='activities', null=False, blank=False)
