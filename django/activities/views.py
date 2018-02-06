"""Activity view module"""
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, UpdateView, View

from activities.forms import ActivityDetailsForm
from api.helper import (create_new_activity_for_user, get_activity_by_id,
                        verify_private_owner)
from api.models import Activity, ActivityTrack
from core import UNIT_SETTING, DATETIME_FORMAT_STR
from core.views import UploadFormMixin
from core.forms import (UploadFileForm,
                        ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


class UploadView(View):
    """Upload view"""

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        """Handle post request"""
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity = create_new_activity_for_user(user=request.user)
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('activities:details', activity.id)
        else:
            raise SuspiciousOperation


class UploadTrackView(View):
    """Upload track view"""

    def post(self, request: HttpRequest, activity_id: int) -> \
            HttpResponseRedirect:
        """Handle post request"""
        activity = get_activity_by_id(activity_id)

        # Check to see if current user owns this activity, if not 403
        if request.user != activity.user:
            raise PermissionDenied

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('activities:view_activity', pk=activity.id)
        else:
            raise SuspiciousOperation


class DetailsView(UpdateView):
    """Activity details updating view"""
    model = Activity
    template_name = 'activity_details.html'
    form_class = ActivityDetailsForm

    def get_object(self, queryset: QuerySet = None) -> Activity:
        """Get activity, only allowing owner to see private activities"""
        activity = super(DetailsView, self).get_object(queryset)
        if self.request.user != activity.user:
            raise PermissionDenied
        return activity

    def get_form_kwargs(self):
        """Get custom form kwargs"""
        kwargs = super(DetailsView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(DetailsView, self).get_context_data(**kwargs)
        if self.object.name is None:
            cancel_link = reverse('api:delete_activity', args=[self.object.id])
        else:
            cancel_link = reverse('activities:view_activity',
                                  args=[self.object.id])
        context['cancel_link'] = cancel_link
        context['units'] = UNIT_SETTING
        return context


class ActivityView(UploadFormMixin, DetailView):
    """Activity view"""
    model = Activity
    template_name = 'activity.html'
    context_object_name = 'activity'

    def get_object(self, queryset: QuerySet = None) -> Activity:
        """Get activity, only allowing owner to see private activities"""
        activity = super().get_object(queryset)
        verify_private_owner(activity, self.request)
        return activity

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(ActivityView, self).get_context_data(**kwargs)
        context['val_errors'] = ERRORS
        context['units'] = UNIT_SETTING
        return context


class ActivityTrackView(UploadFormMixin, DetailView):
    """Activity Track view"""
    model = ActivityTrack
    template_name = 'track.html'
    context_object_name = 'track'

    def get_queryset(self):
        queryset = super(ActivityTrackView, self).get_queryset()
        return queryset.select_related('activity')

    def get_object(self, queryset: QuerySet = None) -> ActivityTrack:
        """Get activity, only allowing owner to see private activities"""
        track = super().get_object(queryset)

        if self.request.user != track.activity.user:
            raise PermissionDenied
        return track

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(ActivityTrackView, self).get_context_data(**kwargs)
        context['val_errors'] = ERRORS
        context['units'] = UNIT_SETTING
        context['last_track'] = self.object.activity.tracks.count() == 1
        return context


class ActivityTrackTrimView(ActivityTrackView):
    """Activity Track view"""
    template_name = 'track_trim.html'

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(ActivityTrackTrimView, self).get_context_data(**kwargs)
        track = self.get_object()
        context['start_time'] = track.trim_start.strftime(DATETIME_FORMAT_STR)
        context['end_time'] = track.trim_end.strftime(DATETIME_FORMAT_STR)
        return context


class ActivityTrackDownloadView(DetailView):
    """Activity Track Download view"""
    model = ActivityTrack

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Track original file download view"""
        track = self.get_object()  # type: ActivityTrack

        if request.user != track.activity.user:
            raise PermissionDenied

        filename = track.original_file.file.name.split('/')[-1]
        response = HttpResponse(track.original_file.file,
                                content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
