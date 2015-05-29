from django.db import models
from django.contrib.auth.models import User

from sirf.stats import Stats
from sirf import Parser

import gpxpy

from datetime import datetime as dt
import pytz

import os.path

from activities import UNITS, units, DATETIME_FORMAT_STR

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


class Activity(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    datetime = models.DateTimeField(null=True)
    user = models.ForeignKey(User, related_name='activity', null=False)
    model_distance = models.FloatField(null=True)  # m
    model_max_speed = models.FloatField(null=True)  # m/s
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    category = models.CharField(max_length=2,
                                blank=False,
                                choices=ACTIVITY_CHOICES,
                                default=SAILING)

    class Meta:
        ordering = ['-datetime']

    @property
    def end_time(self):
        return self.track.last().trim_end.time()

    @property
    def start_time(self):
        return self.track.first().trim_start.time()

    @property
    def date(self):
        return self.track.first().trim_start.date()

    @property
    def duration(self):
        return (self.track.last().trim_end -
                self.track.first().trim_start)

    @property
    def max_speed(self):
        if self.model_max_speed is None:
            pos = self.get_trackpoints()
            stats = Stats(pos)
            self.model_max_speed = stats.max_speed.magnitude
            self.save()

        speed = (self.model_max_speed * units.m/units.s).to(UNITS['speed'])
        return '{:~.2f}'.format(speed)

    @property
    def distance(self):
        if self.model_distance is None:
            pos = self.get_trackpoints()
            stats = Stats(pos)
            self.model_distance = stats.distance().magnitude
            self.save()

        dist = (self.model_distance * units.m).to(UNITS['dist'])
        return '{:~.2f}'.format(dist)

    def compute_stats(self):
        pos = self.get_trackpoints()
        stats = Stats(pos)
        self.model_distance = stats.distance().magnitude
        self.model_max_speed = stats.max_speed.magnitude

        self.save()

    def add_track(self, upfile):
        ActivityTrack.create_new(upfile, self)

    def get_trackpoints(self):
        out = []
        for track in self.track.all().order_by("trim_start"):
            out.extend(
                track.get_trackpoints()
                     .values('sog', 'lat', 'lon', 'timepoint'))
        return out


class ActivityTrack(models.Model):
    original_filename = models.CharField(max_length=255, null=False,
                                         blank=False)
    trim_start = models.DateTimeField(null=True, default=None)
    trim_end = models.DateTimeField(null=True, default=None)
    trimmed = models.BooleanField(null=False, default=False)
    activity_id = models.ForeignKey(Activity, related_name='track',
                                    blank=False, null=False)

    class Meta:
        ordering = ['trim_start']

    def initialize_stats(self):
        self.reset_trim()

        if self.activity_id.datetime is None:
            self.activity_id.datetime = self.trim_start
            self.activity_id.save()
        elif self.activity_id.datetime > self.trim_start:
            self.activity_id.datetime = self.trim_start
            self.activity_id.save()

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
            self.activity_id.compute_stats()

    def reset_trim(self):
        self.trim_start = self.trackpoint.first().timepoint
        self.trim_end = self.trackpoint.last().timepoint
        self.trimmed = False
        self.save()
        self.activity_id.compute_stats()

    def get_trackpoints(self):
        return self.trackpoint.filter(
            timepoint__range=(self.trim_start, self.trim_end)
        )

    @staticmethod
    def create_new(upfile, activity_id):
        track = ActivityTrack.objects.create(activity_id=activity_id,
                                             original_filename=upfile.name)
        _create_trackpoints(track, upfile)
        track.initialize_stats()
        return track


def _create_trackpoints(track, upfile):
    filetype = os.path.splitext(upfile.name)[1][1:].upper()

    if filetype == 'SBN':
        _create_sbn_trackpoints(track, upfile)
    elif filetype == 'GPX':
        _create_gpx_trackpoints(track, upfile)
    else:
        raise Exception('Unknown filetype')


def _create_sbn_trackpoints(track, upfile):
    d = Parser()
    d.process(upfile.read())
    d = [x for x in d.pktq
         if x is not None and x['fixtype'] != 'none']  # filter out Nones

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
            track_id=track))
    ActivityTrackpoint.objects.bulk_create(insert)


def _create_gpx_trackpoints(track, upfile):
    gpx = upfile.read().decode('utf-8')
    gpx = gpxpy.parse(gpx)

    insert = []
    app = insert.append  # cache append method for speed.. maybe?

    prev_point = None
    speed = 0

    for gpstrack in gpx.tracks:
        for segment in gpstrack.segments:
            for point in segment.points:
                if prev_point is not None:
                    speed = point.speed_between(prev_point)
                if speed is None:
                    speed = 0
                prev_point = point
                app(ActivityTrackpoint(
                    lat=point.latitude,
                    lon=point.longitude,
                    sog=speed,
                    timepoint=point.time.replace(tzinfo=pytz.UTC),
                    track_id=track))
    ActivityTrackpoint.objects.bulk_create(insert)


class ActivityTrackpoint(models.Model):
    timepoint = models.DateTimeField()
    lat = models.FloatField()  # degrees
    lon = models.FloatField()  # degrees
    sog = models.FloatField()  # m/s
    track_id = models.ForeignKey(ActivityTrack, related_name='trackpoint')
