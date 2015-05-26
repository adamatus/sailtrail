import json

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import numpy as np

from activities import UNITS, units, DATETIME_FORMAT_STR
from .models import Activity, ActivityTrack
from .forms import UploadFileForm, ActivityDetailsForm, NewUserForm
from sirf.stats import Stats

User = get_user_model()


def home_page(request, form=None):
    if form is None:
        form = UploadFileForm()

    activities = Activity.objects.filter(details__isnull=False)

    # Remove private activities for all but the current user
    activities = activities.exclude(
        ~Q(user__username=request.user.username), details__private=True)

    return render(request, 'home.html',
                  {'activities': activities,
                   'form': form
                   })


def activity_list(request, form=None):
    return home_page(request, form)


def user_page(request, username, form=None):
    if form is None:
        form = UploadFileForm()

    activities = Activity.objects.filter(user__username=username).filter(
        details__isnull=False)

    # Filter out private activities is the user is not viewing themselves
    if request.user.username != username:
        activities = activities.filter(details__private=False)

    return render(request, 'user.html',
                  {'activities': activities,
                   'username': username,
                   'form': form
                   })


def user_list(request, form=None):
    users = User.objects.all()
    return render(request, 'user_list.html',
                  {'users': users,
                   'form': form
                   })


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity = Activity.objects.create(user=request.user)
            activity.add_track(request.FILES['upfile'])
            return redirect('details', activity.id)
    else:
        form = UploadFileForm()

    return home_page(request, form=form)


@login_required
def upload_track(request, activity_id):

    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user owns this activity, if not 403
    if request.user != activity.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity.add_track(request.FILES['upfile'])
            return redirect('view_activity', activity.id)
    else:
        form = UploadFileForm({'activity': activity_id})

    return view(request, activity_id, form=form)


@login_required
def details(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    # Only allow the owner of the activity to access details
    if request.user != activity.user:
        raise PermissionDenied

    cancel_link = reverse('view_activity', args=[activity.id])

    if request.method == 'POST':
        request.POST['activity_id'] = activity_id
        if hasattr(activity, 'details'):
            form = ActivityDetailsForm(request.POST, instance=activity.details)
        else:
            form = ActivityDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_activity', activity.id)
    else:
        if hasattr(activity, 'details'):
            form = ActivityDetailsForm(instance=activity.details)
        else:
            form = ActivityDetailsForm()
            cancel_link = reverse('delete_activity', args=[activity.id])
            activity.stats.compute_stats()

    return render(request, 'activity_details.html', {'activity': activity,
                                                     'form': form,
                                                     'cancel_link':
                                                     cancel_link})


def verify_private_owner(activity, request):
    if activity.details.private and request.user != activity.user:
        raise PermissionDenied


def view(request, activity_id, form=None):
    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(activity, request)

    if form is None:
        form = UploadFileForm({'activity': activity_id})

        # Manually remove upfile error that we get when creating
        # the form with a pre-populated activity
        form.errors.pop('upfile')

    print(form.errors)

    return render(request,
                  'activity.html',
                  {'activity': activity,
                   'units': UNITS,
                   'form': form,
                   'owner': request.user == activity.user,
                   })


def activity_json(request, activity_id, form=None):
    activity = Activity.objects.get(id=activity_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(activity, request)

    pos = activity.get_trackpoints()
    return return_json(pos)


def view_track(request, activity_id, track_id, form=None):

    track = ActivityTrack.objects.get(id=track_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(track.activity_id, request)

    if form is None:
        form = UploadFileForm({'activity': activity_id})

    return render(request,
                  'track.html',
                  {'track': track,
                   'activity': track.activity_id,
                   'units': UNITS,
                   'trimmed': track.trimmed,
                   'form': form,
                   })


def track_json(request, activity_id, track_id, form=None):

    track = ActivityTrack.objects.get(id=track_id)

    # Check to see if current user can see this, 403 if necessary
    verify_private_owner(track.activity_id, request)

    pos = list(track.get_trackpoints()
                    .values('sog', 'lat', 'lon', 'timepoint'))

    return return_json(pos)


def return_json(pos):

    stats = Stats(pos)
    distances = stats.distances()
    bearings = stats.bearing()

    # hack to get same size arrays (just repeat final element)
    distances = np.append(distances, distances[-1])
    bearings = np.append(bearings, bearings[-1])

    for i, p in enumerate(pos):
        speed = (p['sog'] * units.m/units.s).to(UNITS['speed']).magnitude
        p['speed'] = round(speed, 2)
        p['time'] = p['timepoint'].strftime(DATETIME_FORMAT_STR)
        p['dist'] = round(distances[i], 3)
        p['bearing'] = round(bearings[i], 2)
        del p['timepoint']
        del p['sog']

    out = dict(details=pos)

    return HttpResponse(json.dumps(out), content_type="application/json")


@login_required
def delete(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    if request.user != activity.user:
        raise PermissionDenied
    activity.delete()
    return redirect('home')


@login_required
def delete_track(request, activity_id, track_id):
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.delete()
    track.activity_id.stats.model_distance = None
    track.activity_id.stats.model_max_speed = None
    track.activity_id.stats.save()
    return redirect('view_activity', activity_id)


@login_required
def trim(request, activity_id, track_id):
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.trim(request.POST['trim-start'], request.POST['trim-end'])
    return redirect('view_activity', activity_id)


@login_required
def untrim(request, activity_id, track_id):
    track = ActivityTrack.objects.get(id=track_id)
    if request.user != track.activity_id.user:
        raise PermissionDenied
    track.reset_trim()
    return redirect('view_activity', activity_id)


def register(request, form=None):
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
