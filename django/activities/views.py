"""Activity view module"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q, Max
from django.shortcuts import render, redirect

from activities import UNIT_SETTING
from api.models import Activity, ActivityTrack, ACTIVITY_CHOICES
from .forms import ActivityDetailsForm
from core.forms import (UploadFileForm,
                        ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

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
