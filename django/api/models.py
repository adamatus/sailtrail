"""Model mapping for activities"""
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Max, Sum, Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from sirf.stats import Stats
from sirf import Parser

import gpxpy

from datetime import datetime as dt
import pytz

import os.path

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR

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
    """Activity model"""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    datetime = models.DateTimeField(null=True)
    user = models.ForeignKey(User, related_name='activity', null=False)
    model_distance = models.FloatField(null=True)  # m
    model_max_speed = models.FloatField(null=True)  # m/s
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True, blank=True)
    private = models.BooleanField(default=False)
    wind_direction = models.FloatField(null=True)
    category = models.CharField(max_length=2,
                                blank=False,
                                choices=ACTIVITY_CHOICES,
                                default=SAILING)

    class Meta:
        ordering = ['-datetime']

    def get_absolute_url(self):
        """Get the URL path for this activity"""
        return reverse('view_activity', args=[str(self.id)])

    @property
    def start_time(self):
        """Get the start time for the activity"""
        return self.track.first().trim_start.time()

    @property
    def end_time(self):
        """Get the ending time for the activity"""
        return self.track.last().trim_end.time()

    @property
    def date(self):
        """Get the start date for the activity"""
        return self.track.first().trim_start.date()

    @property
    def duration(self):
        """Get the duration for the activity"""
        return (self.track.last().trim_end -
                self.track.first().trim_start)

    @property
    def max_speed(self):
        """Get the max speed for the activity"""
        if self.model_max_speed is None:
            pos = self.get_trackpoints()
            stats = Stats(pos)
            self.model_max_speed = stats.max_speed.magnitude
            self.save()

        speed = (self.model_max_speed * UNITS.m / UNITS.s).to(
            UNIT_SETTING['speed'])
        return '{:~.2f}'.format(speed)

    @property
    def distance(self):
        """Get the dirance for the activity"""
        if self.model_distance is None:
            pos = self.get_trackpoints()
            stats = Stats(pos)
            self.model_distance = stats.distance().magnitude
            self.save()

        dist = (self.model_distance * UNITS.m).to(UNIT_SETTING['dist'])
        return '{:~.2f}'.format(dist)

    def compute_stats(self):
        """Compute the activity stats"""
        pos = self.get_trackpoints()
        stats = Stats(pos)
        self.model_distance = stats.distance().magnitude
        self.model_max_speed = stats.max_speed.magnitude

        self.save()

    def add_track(self, upfile):
        """Add a new track to the activity

        Parameters
        ----------
        upfile : file
        """
        ActivityTrack.create_new(upfile, self)

    def get_trackpoints(self):
        """Helper to return the trackpoints"""
        out = []
        for track in self.track.all().order_by("trim_start"):
            out.extend(
                track.get_trackpoints().values('sog', 'lat',
                                               'lon', 'timepoint'))
        return out


class ActivityTrack(models.Model):
    """Activity Track model"""
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
        """Initialize activity stats"""

        self.reset_trim()

        if self.activity_id.datetime is None:
            self.activity_id.datetime = self.trim_start
            self.activity_id.save()
        elif self.activity_id.datetime > self.trim_start:
            self.activity_id.datetime = self.trim_start
            self.activity_id.save()

    def trim(self, trim_start=-1, trim_end=-1):
        """Trim the activity to the given time interval

        Parameters
        ----------
        trim_start
           The timepoint to start the trim at
        trim_end
           The timepoint to end the trim at
        """

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
        """Reset the track trim"""
        self.trim_start = self.trackpoint.first().timepoint
        self.trim_end = self.trackpoint.last().timepoint
        self.trimmed = False
        self.save()
        self.activity_id.compute_stats()

    def get_trackpoints(self):
        """Get sorted trackpoints for an activity"""
        return self.trackpoint.filter(
            timepoint__range=(self.trim_start, self.trim_end)
        ).order_by('timepoint')

    @staticmethod
    def create_new(upfile, activity_id):
        """Create a new activity

        Parameters
        ----------
        upfile : file
            The file to upload
        activity_id : int
            The activity id
        """
        track = ActivityTrack.objects.create(activity_id=activity_id,
                                             original_filename=upfile.name)
        _create_trackpoints(track, upfile)
        track.initialize_stats()
        return track


def _create_trackpoints(track, upfile):
    """Create trackpoints from file

    Parameters
    ----------
    track : int
    upfile : file

    """
    filetype = os.path.splitext(upfile.name)[1][1:].upper()

    if filetype == 'SBN':
        _create_sbn_trackpoints(track, upfile)
    elif filetype == 'GPX':
        _create_gpx_trackpoints(track, upfile)
    else:
        raise Exception('Unknown filetype')


def _create_sbn_trackpoints(track, upfile):
    """Parse SBN trackpoints

    Parameters
    ----------
    upfile : file
    track : int
    """
    data = Parser()
    data.process(upfile.read())
    # filter out Nones
    data = [x for x in data.pktq if x is not None and x['fixtype'] != 'none']

    insert = []
    app = insert.append  # cache append method for speed.. maybe?
    fmt = '%H:%M:%S %Y/%m/%d'
    for track_point in data:
        app(ActivityTrackpoint(
            lat=track_point['latitude'],
            lon=track_point['longitude'],
            sog=track_point['sog'],
            timepoint=dt.strptime('{} {}'.format(track_point['time'],
                                                 track_point['date']),
                                  fmt).replace(tzinfo=pytz.UTC),
            track_id=track))
    ActivityTrackpoint.objects.bulk_create(insert)


def _create_gpx_trackpoints(track, upfile):
    """Parse GPX trackpoints

    Parameters
    ----------
    track : int
    upfile : file
    """
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
    """Individual activity trackpoint"""
    timepoint = models.DateTimeField()
    lat = models.FloatField()  # degrees
    lon = models.FloatField()  # degrees
    sog = models.FloatField()  # m/s
    track_id = models.ForeignKey(ActivityTrack, related_name='trackpoint')


class Helper(object):
    """Helper methods to access model objects

    Methods to perform queries, etc. Easy to mock"""

    @staticmethod
    def get_users_activities(user, cur_user):
        """Get list of activities, including private activities if cur user"""
        activities = Activity.objects.filter(
            user__username=user.username)

        # Filter out private activities if the user is not viewing themselves
        if cur_user.username != user.username:
            activities = activities.filter(private=False)

        return activities

    @staticmethod
    def summarize_by_category(activities):
        """Summarize activities by category"""
        return activities.values('category').annotate(
            count=Count('category'),
            max_speed=Max('model_max_speed'),
            total_dist=Sum('model_distance')).order_by('-max_speed')

    @staticmethod
    def get_leaders():
        """Build list of leaders for the leaderboard"""
        leader_list = Activity.objects.filter(private=False).values(
            'user__username', 'category').annotate(
                max_speed=Max('model_max_speed')).order_by('-max_speed')

        leaders = []

        for key, category in ACTIVITY_CHOICES:
            values = [x for x in leader_list if x['category'] == key]
            if len(values) > 0:
                leaders.append({'category': category, 'leaders': values})

        return leaders

    @staticmethod
    def get_activities(cur_user):
        """Get activities, include current users private activities"""
        activities = Activity.objects.exclude(name__isnull=True)

        # Remove private activities for all but the current user
        return activities.exclude(
            ~Q(user__username=cur_user.username), private=True)

    @staticmethod
    def verify_private_owner(activity, request):
        """Helper to verify private ownership"""

        # Convert track to activity, if necessary
        if isinstance(activity, ActivityTrack):
            activity = activity.activity_id

        if activity.private and request.user != activity.user:
            raise PermissionDenied