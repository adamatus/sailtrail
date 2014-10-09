from django.shortcuts import render, redirect
from activities.models import Activity
from .forms import UploadFileForm, NewActivityForm


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
            return redirect('new_activity', activity.id)
    else:
        form = UploadFileForm()

    return home_page(request, form=form)


def new(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    if request.method == 'POST':
        request.POST['file_id'] = activity_id
        form = NewActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_activity', activity.id)
    else:
        form = NewActivityForm()
        
    return render(request, 'new_activity.html', {'activity': activity,
                                                 'form': form})


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    return render(request, 'activity.html', {'activity': activity})


def delete(request, activity_id):
    Activity.objects.get(id=activity_id).delete()
    return redirect('home')
   
