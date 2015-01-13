from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from activities.models import Activity
from .forms import UploadFileForm, ActivityDetailsForm

from activities import UNITS, units, DATETIME_FORMAT_STR


def home_page(request, form=None):
    if form is None:
        # form = UploadFileForm()
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
            activity = Activity.objects.create()
            activity.add_track(request.FILES['upfile'])
            return redirect('details', activity.id)
    else:
        form = UploadFileForm()

    return home_page(request, form=form)


def details(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
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


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    pos = activity.get_trackpoints()
    for p in pos:
        p['speed'] = (p['sog'] * units.m/units.s).to(UNITS['speed']).magnitude
        p['time'] = p['timepoint'].strftime(DATETIME_FORMAT_STR)
        del p['timepoint']
        del p['sog']

    return render(request,
                  'activity.html',
                  {'activity': activity,
                   'pos_json': pos,
                   'units': UNITS,
                   })


def delete(request, activity_id):
    Activity.objects.get(id=activity_id).delete()
    return redirect('home')


def trim(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    activity.track.trim(request.POST['trim-start'], request.POST['trim-end'])
    return redirect('view_activity', activity.id)


def untrim(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    activity.track.reset_trim()
    return redirect('view_activity', activity.id)
