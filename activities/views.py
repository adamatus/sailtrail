from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from activities.models import Activity, ActivityStat
from .forms import UploadFileForm, ActivityDetailsForm
from sirf.stats import Stats

import os.path

from activities import UNITS


def home_page(request, form=None):
    if form is None:
        form = UploadFileForm()
    return render(request, 'home.html', 
                  {'activities': 
                      Activity.objects.filter(details__isnull=False), 
                   'form': form
                   })


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save()
            return redirect('details', activity.id)
    else:
        form = UploadFileForm()

    return home_page(request, form=form)


def details(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    cancel_link = reverse('view_activity', args=[activity.id])

    if request.method == 'POST':
        request.POST['file_id'] = activity_id
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
            _compute_stats(activity_id)
        
    return render(request, 'activity_details.html', {'activity': activity,
                                                     'form': form,
                                                     'cancel_link':
                                                     cancel_link})


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    if os.path.exists(activity.upfile.path):
        stats = Stats(activity.upfile.path)
        pos = stats.tracks
        start_sel = 0 if activity.trim_start is None else activity.trim_start
        end_sel = (len(pos)) if activity.trim_end is None \
            else activity.trim_end + 1
        pos = pos[start_sel:end_sel]
        trimmed = activity.trim_start is not None or \
            activity.trim_end is not None
        for p in pos:
            p['speed'] = p['speed'].to(UNITS['speed']).magnitude
    else:
        pos = None
    return render(request, 
                  'activity.html', 
                  {'activity': activity,
                   'pos_json': pos,
                   'units': UNITS,
                   'trimmed': trimmed,
                   })


def delete(request, activity_id):
    Activity.objects.get(id=activity_id).delete()
    return redirect('home')


def trim(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    do_save = False
    if request.POST['trim-start'] is not -1:
        activity.trim_start = request.POST['trim-start']
        do_save = True
    if request.POST['trim-end'] is not -1:
        activity.trim_end = request.POST['trim-end']
        do_save = True
    if do_save:
        activity.save()
    return redirect('view_activity', activity.id)


def untrim(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    activity.trim_start = None
    activity.trim_end = None
    activity.save()
    return redirect('view_activity', activity.id)


def _compute_stats(activity_id):
    activity = Activity.objects.get(id=activity_id)
    if os.path.exists(activity.upfile.path):
        stats = Stats(activity.upfile.path)

        ActivityStat.objects.create(
            datetime=stats.full_start_time,
            duration=stats.duration,
            file_id=activity)  

