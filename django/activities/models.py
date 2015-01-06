from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

from sirf.stats import Stats
from sirf import read_sbn

from datetime import datetime as dt
import pytz

import os.path

from activities import UNITS, units, DATETIME_FORMAT_STR


class Activity(models.Model):
    upfile = models.FileField(upload_to='activities', null=False, blank=False)
    trim_start = models.DateTimeField(null=True, default=None)
    trim_end = models.DateTimeField(null=True, default=None)
    trimmed = models.BooleanField(null=False, default=False)

    class Meta:
        ordering = ['-trim_start']

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
            ActivityStat.objects.create(file_id=self)
            self.reset_trim()

    def trim(self, trim_start=-1, trim_end=-1):
        """Trim the activity to the given time interval"""

        do_save = False

        if trim_start is not -1:
            try:
                self.trim_start = dt.strptime(trim_start, DATETIME_FORMAT_STR)
                do_save = True
            except ValueError:
                # Silently ignore bad input
                pass

        if trim_end is not -1:
            try:
                self.trim_end = dt.strptime(trim_end, DATETIME_FORMAT_STR)
                do_save = True
            except ValueError:
                # Silently ignore bad input
                pass

        # Swap the trim points if they are backwards
        if trim_start is not -1 and trim_end is not -1:
            if self.trim_start > self.trim_end:
                self.trim_start, self.trim_end = self.trim_end, self.trim_start

        if do_save:
            self.trimmed = True
            self.save()
            self.stats.compute_stats()

    def reset_trim(self):
        self.trim_start = self.trackpoint.first().timepoint
        self.trim_end = self.trackpoint.last().timepoint
        self.trimmed = False
        self.save()
        self.stats.compute_stats()

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
    model_distance = models.FloatField(null=True)  # m
    model_max_speed = models.FloatField(null=True)  # m/s

    @property
    def end_time(self):
        return self.file_id.trim_end.time()

    @property
    def start_time(self):
        return self.file_id.trim_start.time()

    @property
    def date(self):
        return self.file_id.trim_start.date()

    @property
    def duration(self):
        return self.file_id.trim_end - self.file_id.trim_start

    @property
    def max_speed(self):
        if self.model_max_speed is None:
            pos = list(self.file_id.get_trackpoints().values('sog',
                                                             'lat',
                                                             'lon',
                                                             'timepoint'))
            stats = Stats(pos)
            self.model_max_speed = stats.max_speed.magnitude
            self.save()

        speed = (self.model_max_speed * units.m/units.s).to(UNITS['speed'])
        return '{:~.2f}'.format(speed)

    @property
    def distance(self):
        if self.model_distance is None:
            pos = list(self.file_id.get_trackpoints().values('sog',
                                                             'lat',
                                                             'lon',
                                                             'timepoint'))
            stats = Stats(pos)
            self.model_distance = stats.distance().magnitude
            self.save()

        dist = (self.model_distance * units.m).to(UNITS['dist'])
        return '{:~.2f}'.format(dist)

    def compute_stats(self):
        pos = list(self.file_id.get_trackpoints().values('sog',
                                                         'lat',
                                                         'lon',
                                                         'timepoint'))
        stats = Stats(pos)
        self.model_distance = stats.distance().magnitude
        self.model_max_speed = stats.max_speed.magnitude

        self.save()
