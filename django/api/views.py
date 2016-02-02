"""Activity view module"""
import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.generic.detail import BaseDetailView

from analysis.track_analysis import make_json_from_trackpoints
from api.helper import verify_private_owner
from api.models import Activity, ActivityTrack
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

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

    def return_json(self):
        """Return the data to be serialized to JSON"""
        raise NotImplementedError("Sub-classes must implement this method")

    def get_object(self, queryset=None):
        """Get the object"""
        the_object = super(BaseJSONView, self).get_object(queryset=queryset)
        verify_private_owner(the_object, self.request)
        return the_object

    def render_to_response(self, context, **response_kwargs):
        """Render to response"""
        return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        """Get the context data, populating the data_field with data"""
        context = super(BaseJSONView, self).get_context_data(**kwargs)
        context[self.data_field] = self.return_json()
        return context


class TrackJSONMixin(object):
    """Mixin to handle the conversion of trackpoint data to desired output"""

    def get_trackpoints(self):
        """Return the specific trackpoints to include"""
        raise NotImplementedError("Sub-classes must implement this method")

    def return_json(self) -> dict:
        """Helper method to return JSON data for trackpoints"""
        return make_json_from_trackpoints(self.get_trackpoints())


class ActivityJSONView(TrackJSONMixin, BaseJSONView):
    """Activity trackpoint JSON view"""
    model = Activity
    data_field = 'pos'

    def get_trackpoints(self):
        """Get the activity trackpoints"""
        return self.get_object().get_trackpoints()


class TrackJSONView(TrackJSONMixin, BaseJSONView):
    """Track trackpoint JSON view"""
    model = ActivityTrack
    data_field = 'pos'

    def get_trackpoints(self):
        """Get the track trackpoints"""
        return list(self.get_object().get_trackpoints().values('sog',
                                                               'lat',
                                                               'lon',
                                                               'timepoint'))


class FullTrackJSONView(TrackJSONMixin, BaseJSONView):
    """Track trackpoint JSON view"""
    model = ActivityTrack
    data_field = 'pos'

    def get_trackpoints(self):
        """Get the track trackpoints"""
        trackpoints = self.get_object().get_trackpoints(filtered=False)
        return list(trackpoints.values('sog', 'lat', 'lon', 'timepoint'))


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
        if self.request.user != track.activity.user:
            raise PermissionDenied
        return track


class DeleteTrackView(BaseTrackView):
    """Delete track view"""
    model = ActivityTrack

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        track = self.get_object()
        track.delete()
        return redirect('view_activity', track.activity_id)


class TrimView(BaseTrackView):
    """Trim track view"""
    model = ActivityTrack

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        track = self.get_object()
        track.trim(request.POST.get('trim-start', '-1'),
                   request.POST.get('trim-end', '-1'))
        return redirect('view_activity', track.activity_id)


class UntrimView(BaseTrackView):
    """Untrim track view"""
    model = ActivityTrack

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Reset the track to be untrimmed"""
        track = self.get_object()
        track.reset_trim()
        return redirect('view_activity', track.activity_id)
