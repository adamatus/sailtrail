"""Activity view module"""
import json

from django.shortcuts import render, redirect, render_to_response
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max, Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import numpy as np

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR
from .models import Activity, ActivityTrack, ACTIVITY_CHOICES
from .forms import (UploadFileForm, ActivityDetailsForm, NewUserForm,
                    ERROR_NO_UPLOAD_FILE_SELECTED,
                    ERROR_UNSUPPORTED_FILE_TYPE)
from sirf.stats import Stats

USER = get_user_model()

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


def get_leaders():
    """GET request to the leaderboard"""
    leader_list = Activity.objects.filter(private=False).values(
        'user__username', 'category').annotate(
            max_speed=Max('model_max_speed')).order_by('-max_speed')

    leaders = []

    for key, category in ACTIVITY_CHOICES:
        values = [x for x in leader_list if x['category'] == key]
        if len(values) > 0:
            leaders.append({'category': category, 'leaders': values})

    return leaders


def home_page(request, form=None):
    """ Handle requests for home page
    Parameters
    ----------
    request
    form

    Returns
    -------

    """
    if form is None:
        form = UploadFileForm()

    activities = Activity.objects.exclude(name__isnull=True)

    # Remove private activities for all but the current user
    activities = activities.exclude(
        ~Q(user__username=request.user.username), private=True)

    return render(request, 'home.html',
                  {'activities': activities,
                   'form': form,
                   'leaders': get_leaders(),
                   'val_errors': ERRORS})


def leaderboards(request):
    """
    Leaderboard view handler

    Parameters
    ----------
    request

    Returns
    -------

    """
    return render(request, 'leaderboards.html', {'leaders': get_leaders()})


def activity_list(request, form=None):
    """
    Activity list view handler

    Parameters
    ----------
    request
    form

    Returns
    -------

    """
    return home_page(request, form)


def user_page(request, username, form=None):
    """
    Individual user page view handler

    Parameters
    ----------
    request
    username
    form

    Returns
    -------

    """
    if form is None:
        form = UploadFileForm()

    activities = Activity.objects.filter(user__username=username)

    # Filter out private activities if the user is not viewing themselves
    if request.user.username != username:
        activities = activities.filter(private=False)

    # Summarize activities by category
    summary = activities.values('category').annotate(
        count=Count('category'),
        max_speed=Max('model_max_speed'),
        total_dist=Sum('model_distance')).order_by('-max_speed')

    return render(request, 'user.html',
                  {'activities': activities,
                   'username': username,
                   'summaries': summary,
                   'form': form})


def user_list(request, form=None):
    """User list view handler.

    Parameters
    ----------
    request
    form

    Returns
    -------

    """
    users = USER.objects.all()
    return render(request, 'user_list.html',
                  {'users': users,
                   'form': form})


@login_required
def upload(request):
    """Upload handler

    Parameters
    ----------
    request

    Returns
    -------

    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity = Activity.objects.create(user=request.user)
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('details', activity.id)
    else:
        form = UploadFileForm()

    return home_page(request, form=form)


@login_required
def upload_track(request, activity_id):
    """Upload track handler

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
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('view_activity', activity.id)
    else:
        form = UploadFileForm()

    return view(request, activity_id, form=form)


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


@login_required
def details(request, activity_id):
    """ Activity detail view handler

    Parameters
    ----------
    request
    activity_id

    Returns
    -------

    """
    activity = Activity.objects.get(id=activity_id)

    # Only allow the owner of the activity to access details
    if request.user != activity.user:
        raise PermissionDenied

    cancel_link = reverse('view_activity', args=[activity.id])

    if request.method == 'POST':
        request.POST['activity_id'] = activity_id
        form = ActivityDetailsForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('view_activity', activity.id)
        else:
            if activity.name is None:
                cancel_link = reverse('delete_activity', args=[activity.id])

    else:
        form = ActivityDetailsForm(instance=activity)
        if activity.name is None:
            cancel_link = reverse('delete_activity', args=[activity.id])
            activity.compute_stats()

    return render(request, 'activity_details.html', {'activity': activity,
                                                     'units': UNIT_SETTING,
                                                     'form': UploadFileForm(),
                                                     'detail_form': form,
                                                     'cancel_link':
                                                     cancel_link})


def verify_private_owner(activity, request):
    """Helper to verify private ownership

    Parameters
    ----------
    activity
    request
    """
    if activity.private and request.user != activity.user:
        raise PermissionDenied


def view(request, activity_id, form=None):
    """Activity view handler

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

    if form is None:
        form = UploadFileForm()

    return render(request,
                  'activity.html',
                  {'activity': activity,
                   'units': UNIT_SETTING,
                   'form': form,
                   'val_errors': ERRORS,
                   'owner': request.user == activity.user})


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


def view_track(request, activity_id, track_id, form=None):
    """Track view handler

    Parameters
    ----------
    activity_id
    request
    track_id
    form

    Returns
    -------
    """
    del activity_id  # delete activity_id as it is not attached to track

    track = ActivityTrack.objects.get(id=track_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(track.activity_id, request)

    if form is None:
        form = UploadFileForm()

    return render(request,
                  'track.html',
                  {'track': track,
                   'activity': track.activity_id,
                   'units': UNIT_SETTING,
                   'trimmed': track.trimmed,
                   'val_errors': ERRORS,
                   'form': form})


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


def register(request, form=None):
    """Register user handler

    Parameters
    ----------
    request
    form

    Returns
    -------

    """
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password2")
            form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        if form is None:
            form = NewUserForm()
    return render(request, 'register.html',
                  {'form': form})


# Test sending email

def send_email(request):
    if request.method == 'POST':
        try:
            subject = request.POST['subject']
            message = request.POST['message']
            from_email = request.POST['from']
            html_message = bool(request.POST.get('html-message', False))
            recipient_list = [request.POST['to']]

            email = EmailMessage(subject, message, from_email, recipient_list)
            if html_message:
                email.content_subtype = 'html'
            email.send()
        except KeyError:
            return HttpResponse('Please fill in all fields')

        return HttpResponse('Email sent :)')
    else:
        return render(request, 'send-email.html')
