from django.shortcuts import render, redirect
from activities.models import Activity
import os.path


def home_page(request):
    return render(request, 'home.html', {'activities': Activity.objects.all()})


def upload(request):
    path, name = os.path.split(request.POST['filename'])
    Activity.objects.create(filename=name, filepath=path)
    return redirect('home')


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    return render(request, 'activity.html', {'activity': activity})
