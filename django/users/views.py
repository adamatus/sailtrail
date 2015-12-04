"""Activity view module"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Max, Sum
from django.shortcuts import render

from api.models import Activity
from core.forms import (UploadFileForm,
                        ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

USER = get_user_model()

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


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
