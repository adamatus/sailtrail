from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from activities.models import Activity
from .forms import UploadFileForm, ActivityDetailsForm

from activities import UNITS, units


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
            activity.stats.compute_stats()

    return render(request, 'activity_details.html', {'activity': activity,
                                                     'form': form,
                                                     'cancel_link':
                                                     cancel_link})


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    trimmed = activity.trimmed

    pos = list(activity.get_trackpoints().values('sog',
                                                 'lat',
                                                 'lon',
                                                 'timepoint'))
    for p in pos:
        p['speed'] = (p['sog'] * units.m/units.s).to(UNITS['speed']).magnitude
        p['time'] = p['timepoint'].isoformat()
        del p['timepoint']
        del p['sog']

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
    activity.trim(request.POST['trim-start'], request.POST['trim-end'])
    return redirect('view_activity', activity.id)


def untrim(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    activity.reset_trim()
    return redirect('view_activity', activity.id)
