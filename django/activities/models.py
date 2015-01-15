from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from sirf.stats import Stats
from sirf import read_sbn

from datetime import datetime as dt
import pytz

import os.path

from activities import UNITS, units, DATETIME_FORMAT_STR


class Activity(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def add_track(self, upfile):
        ActivityTrack.objects.create(upfile=upfile, activity_id=self)

    def get_trackpoints(self):
        out = []
        for track in self.track.all().order_by("trim_start"):
            out.extend(
                track.get_trackpoints()
                     .values('sog', 'lat', 'lon', 'timepoint'))
        return out


class ActivityTrack(models.Model):
    upfile = models.FileField(upload_to='activities', null=False, blank=False)
    trim_start = models.DateTimeField(null=True, default=None)
    trim_end = models.DateTimeField(null=True, default=None)
    trimmed = models.BooleanField(null=False, default=False)
    activity_id = models.ForeignKey(Activity, related_name='track',
                                    blank=False, null=False)

    class Meta:
        ordering = ['trim_start']

    def save(self, *args, **kwargs):
        super(ActivityTrack, self).save(*args, **kwargs)

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
                    track_id=self))
            ActivityTrackpoint.objects.bulk_create(insert)

            # Create stats model entry if necessary
            try:
                self.activity_id.stats.compute_stats()
            except ObjectDoesNotExist:
                ActivityStat.objects.create(activity_id=self.activity_id)
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
            self.activity_id.stats.compute_stats()

    def reset_trim(self):
        self.trim_start = self.trackpoint.first().timepoint
        self.trim_end = self.trackpoint.last().timepoint
        self.trimmed = False
        self.save()
        self.activity_id.stats.compute_stats()

    def get_trackpoints(self):
        return self.trackpoint.filter(
            timepoint__range=(self.trim_start, self.trim_end)
        )


@receiver(post_delete, sender=ActivityTrack)
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
    track_id = models.ForeignKey(ActivityTrack, related_name='trackpoint')


class ActivityDetail(models.Model):
    SAILING = 'SL'
    WINDSURFING = 'WS'
    KITEBOARDING = 'KB'
    SNOWKITING = 'SK'
    ICEBOATING = 'IB'
    ACTIVITY_CHOICES = (
        (SAILING, 'Sailing'),
        (WINDSURFING, 'Windsurfing'),
        (KITEBOARDING, 'Kite Boarding'),
        (SNOWKITING, 'Snow Kiting'),
        (ICEBOATING, 'Ice Boating'),
    )

    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    activity_id = models.OneToOneField(Activity, related_name='details',
                                       blank=False, null=False)
    category = models.CharField(max_length=2,
                                blank=False,
                                choices=ACTIVITY_CHOICES,
                                default=SAILING)


class ActivityStat(models.Model):
    activity_id = models.OneToOneField(Activity, related_name='stats',
                                       blank=False, null=False)
    model_distance = models.FloatField(null=True)  # m
    model_max_speed = models.FloatField(null=True)  # m/s

    @property
    def end_time(self):
        print('Track:', self.activity_id)
        return self.activity_id.track.last().trim_end.time()

    @property
    def start_time(self):
        return self.activity_id.track.first().trim_start.time()

    @property
    def date(self):
        return self.activity_id.track.first().trim_start.date()

    @property
    def duration(self):
        return (self.activity_id.track.last().trim_end -
                self.activity_id.track.first().trim_start)

    @property
    def max_speed(self):
        if self.model_max_speed is None:
            pos = self.activity_id.get_trackpoints()
            stats = Stats(pos)
            self.model_max_speed = stats.max_speed.magnitude
            self.save()

        speed = (self.model_max_speed * units.m/units.s).to(UNITS['speed'])
        return '{:~.2f}'.format(speed)

    @property
    def distance(self):
        if self.model_distance is None:
            pos = self.activity_id.get_trackpoints()
            stats = Stats(pos)
            self.model_distance = stats.distance().magnitude
            self.save()

        dist = (self.model_distance * units.m).to(UNITS['dist'])
        return '{:~.2f}'.format(dist)

    def compute_stats(self):
        pos = self.activity_id.get_trackpoints()
        stats = Stats(pos)
        self.model_distance = stats.distance().magnitude
        self.model_max_speed = stats.max_speed.magnitude

        self.save()
