"""Activity view module"""
import json

import numpy as np
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponse, HttpRequest, JsonResponse
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
        verify_private_owner(activity, request)
        return HttpResponse(
            json.dumps(dict(wind_direction=activity.wind_direction)),
            content_type="application/json")


class JSONResponseMixin(object):
    """Mixin to render response as JsonResponse"""
    data_field = None

    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """Render response as JSON"""
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """Get the data that will be serialized to JSON"""
        return context[self.data_field]


class BaseJSONView(JSONResponseMixin, BaseDetailView):
    """Base detail JSON view"""
    data_field = 'json'

    def get_object(self, queryset=None):
        """Get the object"""
        the_object = super(BaseJSONView, self).get_object()
        verify_private_owner(the_object, self.request)
        return the_object

    def render_to_response(self, context, **response_kwargs):
        """Render to response"""
        return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        """Get the context data, populating the data_field with data"""
        context = super(BaseJSONView, self).get_context_data(**kwargs)
        context[self.data_field] = return_json(self.get_json())
        return context


class ActivityJSONView(BaseJSONView):
    """Activity trackpoint JSON view"""
    model = Activity
    data_field = 'pos'

    def get_json(self):
        """Get the activity trackpoints"""
        return self.get_object().get_trackpoints()


class TrackJSONView(BaseJSONView):
    """Track trackpoint JSON view"""
    model = ActivityTrack
    data_field = 'pos'

    def get_json(self):
        """Get the track trackpoints"""
        return list(self.get_object().get_trackpoints().values('sog',
                                                               'lat',
                                                               'lon',
                                                               'timepoint'))


def return_json(pos: list) -> dict:
    """Helper method to return JSON data"""

    stats = Stats(pos)
    # distances = stats.distances()
    bearings = stats.bearing()

    # hack to get same size arrays (just repeat final element)
    # distances = np.round(np.append(distances, distances[-1]), 3)
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

    return dict(bearing=bearings.tolist(), time=time,
                speed=speed, lat=lat, lon=lon)


class DeleteActivityView(BaseDetailView):
    """Delete activity view"""
    model = Activity

    def get_object(self, queryset=None) -> Activity:
        """Get the activity"""
        activity = super(DeleteActivityView, self).get_object(
            queryset=queryset)
        if self.request.user != activity.user:
            raise PermissionDenied
        return activity

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Delete the activity"""
        self.get_object().delete()
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
        track = self.get_object()
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
