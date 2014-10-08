from django.shortcuts import render, redirect
from activities.models import Activity
from .forms import UploadFileForm


def home_page(request):
    return render(request, 'home.html', 
                  {'activities': Activity.objects.all(),
                   'form': UploadFileForm()
                   })


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UploadFileForm()

    return render(request, 'home.html', 
                  {'activities': Activity.objects.all(),
                   'form': form,
                   })


def view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    return render(request, 'activity.html', {'activity': activity})


def delete(request, activity_id):
    Activity.objects.get(id=activity_id).delete()
    return redirect('home')
   
