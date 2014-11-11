from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

from sirf.stats import Stats
from sirf import read_sbn

import timedelta
from datetime import datetime as dt
import pytz

import os.path

from activities import UNITS, units


class Activity(models.Model):
    upfile = models.FileField(upload_to='activities', null=False, blank=False)
    trim_start = models.DateTimeField(null=True, default=None)
    trim_end = models.DateTimeField(null=True, default=None)
    trimmed = models.BooleanField(null=False, default=False)

    class Meta:
        ordering = ['-stats__datetime']

    def save(self, *args, **kwargs):
        super(Activity, self).save(*args, **kwargs)

        if self.trackpoint.count() == 0:
            d = read_sbn(self.upfile.path)
            d = [x for x in d.pktq if x is not None]  # filter out Nones

            insert = []
            app = insert.append  # cache append method for speed.. maybe?
            for tp in d:
                app(ActivityTrackpoint(
                    lat=tp['latitude'], 
                    lon=tp['longitude'], 
                    sog=tp['sog'], 
                    timepoint=dt.strptime('{} {}'.format(
                        tp['time'], tp['date']),
                        '%H:%M:%S %Y/%m/%d').replace(tzinfo=pytz.UTC),
                    file_id=self))
            ActivityTrackpoint.objects.bulk_create(insert)
            self.reset_trim()

    def reset_trim(self):
            self.trim_start = self.trackpoint.first().timepoint
            self.trim_end = self.trackpoint.last().timepoint
            self.trimmed = False
            self.save()

    def get_trackpoints(self):
        return self.trackpoint.filter(
            timepoint__range=(self.trim_start, self.trim_end)
        )


@receiver(post_delete, sender=Activity)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):
    """Remove file when corresponding model object has been deleted"""
    if instance.upfile:
        if os.path.isfile(instance.upfile.path):
            os.remove(instance.upfile.path)


class ActivityTrackpoint(models.Model):
    timepoint = models.DateTimeField()
    lat = models.FloatField()  # degrees
    lon = models.FloatField()  # degrees
    sog = models.FloatField()  # m/s
    file_id = models.ForeignKey(Activity, related_name='trackpoint')


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
    model_distance = models.FloatField(null=True)  # m
    model_max_speed = models.FloatField(null=True)  # m/s

    @property
    def end_time(self):
        return (self.datetime + self.duration).time()

    @property
    def start_time(self):
        return self.datetime.time()

    @property
    def date(self):
        return self.datetime.date()

    @property
    def max_speed(self):
        if self.model_max_speed is None:
            if os.path.exists(self.file_id.upfile.path):
                stats = Stats(self.file_id.upfile.path)
                self.model_max_speed = stats.max_speed.magnitude
                self.save()
            else:
                return '--error--'

        speed = (self.model_max_speed * units.m/units.s).to(UNITS['speed'])
        return '{:~.2f}'.format(speed)

    @property
    def distance(self):
        if self.model_distance is None:
            if os.path.exists(self.file_id.upfile.path):
                stats = Stats(self.file_id.upfile.path)
                self.model_distance = stats.distance().magnitude
                self.save()
            else:
                return '--error--'

        dist = (self.model_distance * units.m).to(UNITS['dist'])
        return '{:~.2f}'.format(dist)
