from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from activities.models import Activity, ActivityStat
from .forms import UploadFileForm, ActivityDetailsForm
from sirf.stats import Stats

import os.path


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
    return render(request, 'activity.html', {'activity': activity})


def delete(request, activity_id):
    Activity.objects.get(id=activity_id).delete()
    return redirect('home')


def _compute_stats(activity_id):
    activity = Activity.objects.get(id=activity_id)
    if os.path.exists(activity.upfile.path):
        stats = Stats(activity.upfile.path)

        ActivityStat.objects.create(
            datetime=stats.full_start_time,
            duration=stats.duration,
            file_id=activity)  

