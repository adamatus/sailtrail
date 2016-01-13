"""Activity view module"""
import json

import numpy as np
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.detail import BaseDetailView

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR
from api.helper import verify_private_owner
from api.models import Activity, ActivityTrack
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)
from sirf.stats import Stats

USER = get_user_model()

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


class WindDirection(BaseDetailView):
    """Wind direction handler"""
    model = Activity

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Save an updated wind direction"""
        activity = self.get_object()
        if request.user != activity.user:
            raise PermissionDenied
        activity.wind_direction = request.POST['wind_direction']
        activity.save()
        return self.get(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Return wind direction as JSON"""
        activity = self.get_object()
        if request.user != activity.user and activity.private:
            raise PermissionDenied
        return HttpResponse(
            json.dumps(dict(wind_direction=activity.wind_direction)),
            content_type="application/json")


def activity_json(request: HttpRequest, activity_id: int) -> HttpResponse:
    """ Activity JSON data endpoint"""
    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(activity, request)

    pos = activity.get_trackpoints()
    return return_json(pos)


def track_json(request: HttpRequest, activity_id: int, track_id: int) -> \
        HttpResponse:
    """Track data API endpoint handler"""
    del activity_id  # delete activity_id as it is not attached to track

    track = ActivityTrack.objects.get(id=track_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(track.activity_id, request)

    pos = list(track.get_trackpoints().values('sog', 'lat',
                                              'lon', 'timepoint'))

    return return_json(pos)


def return_json(pos: list) -> HttpResponse:
    """Helper method to return JSON data"""

    stats = Stats(pos)
    distances = stats.distances()
    bearings = stats.bearing()

    # hack to get same size arrays (just repeat final element)
    distances = np.round(np.append(distances, distances[-1]), 3)
    bearings = np.round(np.append(bearings, bearings[-1]))
    speed = []
    time = []
    lat = []
    lon = []

    for position in pos:
        lat.append(position['lat'])
        lon.append(position['lon'])
        speed.append(round(
            (position['sog'] * UNITS.m / UNITS.s).to(
                UNIT_SETTING['speed']).magnitude,
            2))
        time.append(position['timepoint'].strftime(DATETIME_FORMAT_STR))

    out = dict(bearing=bearings.tolist(), time=time,
               speed=speed, lat=lat, lon=lon)

    return HttpResponse(json.dumps(out), content_type="application/json")


@login_required
def delete(request: HttpRequest, activity_id: int) -> HttpResponseRedirect:
    """Delete activity handler"""
    activity = Activity.objects.get(id=activity_id)  # type: Activity
    if request.user != activity.user:
        raise PermissionDenied
    activity.delete()
    return redirect('home')


class BaseTrackView(BaseDetailView):
    """Base detail view for track, only allows access to owner"""
    model = ActivityTrack

    def get_object(self, queryset=None) -> ActivityTrack:
        track = super(BaseTrackView, self).get_object(
            queryset=queryset)
        if self.request.user != track.activity_id.user:
            raise PermissionDenied
        return track


class DeleteTrackView(BaseTrackView):
    """Delete track view"""
    model = ActivityTrack

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        track = self.get_object()
        if track.activity_id.track.count() < 2:
            raise SuspiciousOperation("Cannot delete final track in activity")

        track.delete()
        track.activity_id.model_distance = None
        track.activity_id.model_max_speed = None
        track.activity_id.compute_stats()
        return redirect('view_activity', track.activity_id.id)


class TrimView(BaseTrackView):
    """Trim track view"""
    model = ActivityTrack

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        print("Trying to get object...")
        track = self.get_object()
        print("NEVER GETTING HERE")
        track.trim(self.request.POST.get('trim-start', '-1'),
                   self.request.POST.get('trim-end', '-1'))
        return redirect('view_activity', track.activity_id.id)


class UntrimView(BaseTrackView):
    """Untrim track view"""
    model = ActivityTrack

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        track = self.get_object()
        track.reset_trim()
        return redirect('view_activity', track.activity_id.id)
