from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

import timedelta

import os.path


class Activity(models.Model):
    upfile = models.FileField(upload_to='activities', null=False, blank=False)

    class Meta:
        ordering = ['-stats__datetime']


@receiver(post_delete, sender=Activity)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):
    """Remove file when corresponding model object has been deleted"""
    if instance.upfile:
        if os.path.isfile(instance.upfile.path):
            os.remove(instance.upfile.path)


class ActivityDetail(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    file_id = models.OneToOneField(Activity, related_name='details',
                                   blank=False, null=False)


class ActivityStat(models.Model):
    file_id = models.OneToOneField(Activity, related_name='stats',
                                   blank=False, null=False)
    datetime = models.DateTimeField()
    duration = timedelta.fields.TimedeltaField()

    @property
    def end_time(self):
        return (self.datetime + self.duration).time()

    @property
    def start_time(self):
        return self.datetime.time()

    @property
    def date(self):
        return self.datetime.date()


