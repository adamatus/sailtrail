"""Model mapping for activities"""

import os.path
import uuid
from datetime import datetime as dt, time, date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import QuerySet

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR
from analysis.stats import Stats
from gps import gpx, sirf

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

    def get_absolute_url(self) -> str:
        """Get the URL path for this activity"""
        return reverse('view_activity', args=[str(self.id)])

    def _get_tracks(self) -> QuerySet:
        """Trivial helper to use related object to fetch tracks.

        Added to allow for easy mocking of tracks for unit testing"""
        return self.track  # pragma: unit cover ignore

    @property
    def start_time(self) -> time:
        """Get the start time for the activity"""
        return self._get_tracks().first().trim_start.time()

    @property
    def end_time(self) -> time:
        """Get the ending time for the activity"""
        return self._get_tracks().last().trim_end.time()

    @property
    def date(self) -> date:
        """Get the start date for the activity"""
        return self._get_tracks().first().trim_start.date()

    @property
    def duration(self) -> timedelta:
        """Get the duration for the activity"""
        return (self._get_tracks().last().trim_end -
                self._get_tracks().first().trim_start)

    @property
    def max_speed(self) -> str:
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
    def distance(self) -> str:
        """Get the distance for the activity"""
        if self.model_distance is None:
            pos = self.get_trackpoints()
            stats = Stats(pos)
            self.model_distance = stats.distance().magnitude
            self.save()

        dist = (self.model_distance * UNITS.m).to(UNIT_SETTING['dist'])
        return '{:~.2f}'.format(dist)

    def compute_stats(self) -> None:
        """Compute the activity stats"""
        pos = self.get_trackpoints()
        stats = Stats(pos)
        self.model_distance = stats.distance().magnitude
        self.model_max_speed = stats.max_speed.magnitude

        self.save()

    def add_track(self, uploaded_file: InMemoryUploadedFile) -> None:
        """Add a new track to the activity"""
        ActivityTrack.create_new(uploaded_file, self)

    def get_trackpoints(self) -> list:
        """Helper to return the trackpoints"""
        out = []
        for track in self._get_tracks().all().order_by("trim_start"):
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

    def __str__(self):
        """Pretty print the activity track, with original filename included"""
        return "ActivityTrack ({})".format(
            self._get_original_file().file.name)

    def _get_activity(self):
        """Trivial helper to use related object to fetch activity.

        Added to allow for easy mocking of parent activity for unit testing"""
        return self.activity_id  # pragma: unit cover ignore

    def _get_trackpoints(self):
        """Trivial helper to use related object to fetch trackpoints.

        Added to allow for easy mocking of trackpoints for unit testing"""
        return self.trackpoint  # pragma: unit cover ignore

    def _get_original_file(self):
        """Trivial helper to use related object to fetch original file

        Added to allow for easy mocking of parent activity for unit testing"""
        return self.original_file  # pragma: unit cover ignore

    def initialize_stats(self) -> None:
        """Initialize activity stats"""
        self.reset_trim()

        activity = self._get_activity()
        if activity.datetime is None:
            activity.datetime = self.trim_start
            activity.save()
        elif activity.datetime > self.trim_start:
            activity.datetime = self.trim_start
            activity.save()

    def trim(self, trim_start=None, trim_end=None) -> None:
        """Trim the activity to the given time interval

        Parameters
        ----------
        trim_start : str
           The timepoint to start the trim at
        trim_end : str
           The timepoint to end the trim at
        """

        do_save = False

        if trim_start is not None:
            try:
                self.trim_start = dt.strptime(trim_start, DATETIME_FORMAT_STR)
                do_save = True
            except ValueError:
                # Silently ignore bad input
                pass

        if trim_end is not None:
            try:
                self.trim_end = dt.strptime(trim_end, DATETIME_FORMAT_STR)
                do_save = True
            except ValueError:
                # Silently ignore bad input
                pass

        # Swap the trim points if they are backwards
        if (trim_start is not None and trim_end is not None and
                self.trim_start > self.trim_end):
            self.trim_start, self.trim_end = self.trim_end, self.trim_start

        # Don't allow start to equal end
        if self.trim_start == self.trim_end:
            raise SuspiciousOperation("Start and end cannot be same timepoint")

        if do_save:
            # If something changed, make sure we are within the limits
            # of the actual track.  If outside, set to first/last value
            track_start, track_end = self._get_limits()
            if self.trim_start < track_start:
                self.trim_start = track_start
            if self.trim_end > track_end:
                self.trim_end = track_end

            self.trimmed = True
            self.save()
            self._get_activity().compute_stats()

    def reset_trim(self) -> None:
        """Reset the track trim"""
        self.trim_start, self.trim_end = self._get_limits()
        self.trimmed = False
        self.save()
        self._get_activity().compute_stats()

    def _get_limits(self):
        """Return the start and end timepoints of the original track"""
        trackpoint = self._get_trackpoints()
        return trackpoint.first().timepoint, trackpoint.last().timepoint

    def get_trackpoints(self) -> QuerySet:
        """Get sorted, trimmed trackpoints for an activity"""
        return self._get_trackpoints().filter(
            timepoint__range=(self.trim_start, self.trim_end)
        ).order_by('timepoint')

    @staticmethod
    def create_new(upfile: InMemoryUploadedFile, activity_id: int) -> \
            'ActivityTrack':
        """Create a new activity"""
        track = ActivityTrack.objects.create(activity_id=activity_id,
                                             original_filename=upfile.name)
        ActivityTrackFile.objects.create(track=track,
                                         file=upfile)
        upfile.seek(0)
        ActivityTrackpoint.create_trackpoints(track, upfile)
        track.initialize_stats()
        return track


def track_upload_path(instance, filename):  # pylint: disable=unused-argument
    """Return path with UUID for filename"""
    return 'originals/{0}/{1}'.format(uuid.uuid4(), filename)


class ActivityTrackFile(models.Model):
    """Activity track file model"""
    uploaded = models.DateTimeField(auto_now_add=True)
    track = models.OneToOneField(ActivityTrack, related_name='original_file',
                                 on_delete=models.CASCADE)
    file = models.FileField(upload_to=track_upload_path)

    def __str__(self):
        return "ActivityTrackFile ({})".format(self.file)


class ActivityTrackpoint(models.Model):
    """Individual activity trackpoint"""
    timepoint = models.DateTimeField()
    lat = models.FloatField()  # degrees
    lon = models.FloatField()  # degrees
    sog = models.FloatField()  # m/s
    track_id = models.ForeignKey(ActivityTrack, related_name='trackpoint')

    @classmethod
    def create_trackpoints(cls,
                           track: ActivityTrack,
                           uploaded_file: InMemoryUploadedFile):
        """Create trackpoints from file"""
        file_type = os.path.splitext(uploaded_file.name)[1][1:].upper()

        if file_type == 'SBN':
            create_func = sirf.create_trackpoints
        elif file_type == 'GPX':
            create_func = gpx.create_trackpoints
        else:
            raise SuspiciousOperation(
                'Unsupported file type ({})'.format(file_type))

        trackpoints = create_func(track, uploaded_file, cls)
        cls.objects.bulk_create(trackpoints)
