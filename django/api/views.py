"""Activity view module"""
import json

import numpy as np
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR
from api.models import Activity, ActivityTrack, verify_private_owner
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)
from sirf.stats import Stats

USER = get_user_model()

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


@login_required
def wind_direction(request, activity_id):
    """Wind direction handler

    Parameters
    ----------
    request
    activity_id

    Returns
    -------

    """

    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user owns this activity, if not 403
    if request.user != activity.user:
        raise PermissionDenied

    if request.method == 'POST':
        activity.wind_direction = request.POST['wind_direction']
        activity.save()

    return HttpResponse(
        json.dumps(dict(wind_direction=activity.wind_direction)),
        content_type="application/json")


def activity_json(request, activity_id):
    """ Activity JSON data endpoint. TO API

    Parameters
    ----------
    request
    activity_id
    form

    Returns
    -------

    """
    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(activity, request)

    pos = activity.get_trackpoints()
    return return_json(pos)


def track_json(request, activity_id, track_id):
    """Track data API endpoint handler

    Parameters
    ----------
    request
    track_id

    Returns
    -------

    """
    del activity_id  # delete activity_id as it is not attached to track

    track = ActivityTrack.objects.get(id=track_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(track.activity_id, request)

    pos = list(track.get_trackpoints().values('sog', 'lat',
                                              'lon', 'timepoint'))

    return return_json(pos)


def return_json(pos):
    """Helper method to return JSON data
    Parameters
    ----------
    pos

    Returns
    -------

    """

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
def delete(request, activity_id):
    """Delete activity handler

    Parameters
    ----------
    request
    activity_id

    Returns
    -------

    """
    activity = Activity.objects.get(id=activity_id)
    if request.user != activity.user:
        raise PermissionDenied
    activity.delete()
    return redirect('home')


@login_required
def delete_track(request, activity_id, track_id):
    """Delete track handler

    Parameters
    ----------
    request
    activity_id
    track_id

    Returns
    -------

    """
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.delete()
    track.activity_id.model_distance = None
    track.activity_id.model_max_speed = None
    track.activity_id.compute_stats()
    return redirect('view_activity', activity_id)


@login_required
def trim(request, activity_id, track_id):
    """Trim track handler

    Parameters
    ----------
    request
    activity_id
    track_id

    Returns
    -------

    """
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.trim(request.POST['trim-start'], request.POST['trim-end'])
    return redirect('view_activity', activity_id)


@login_required
def untrim(request, activity_id, track_id):
    """Untrim track handler

    Parameters
    ----------
    request
    activity_id
    track_id

    Returns
    -------

    """
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.reset_trim()
    return redirect('view_activity', activity_id)
