"""Activity view module"""
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, UpdateView, View

from .forms import ActivityDetailsForm
from activities import UNIT_SETTING
from api.models import Activity, ActivityTrack, Helper
from core.views import UploadFormMixin
from core.forms import (UploadFileForm,
                        ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


class HomePageView(UploadFormMixin, TemplateView):
    """ Handle requests for home page"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """Update the context with addition homepage data"""
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['activities'] = Helper.get_activities(self.request.user)
        context['leaders'] = Helper.get_leaders()
        context['val_errors'] = ERRORS
        return context


class UploadView(View):
    """Upload view"""

    def post(self, request):
        """Handle post request"""
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            activity = Activity.objects.create(user=request.user)
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('details', activity.id)
        else:
            raise SuspiciousOperation


class UploadTrackView(View):
    """Upload track view"""

    def post(self, request, activity_id):
        """Handle post request"""
        activity = Activity.objects.get(id=activity_id)

        # Check to see if current user owns this activity, if not 403
        if request.user != activity.user:
            raise PermissionDenied

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['upfile']:
                activity.add_track(each)
            return redirect('view_activity', pk=activity.id)
        else:
            raise SuspiciousOperation


class DetailsView(UpdateView):
    """Activity details updating view"""
    model = Activity
    template_name = 'activity_details.html'
    form_class = ActivityDetailsForm

    def get_object(self, queryset=None):
        """Get activity, only allowing owner to see private activities"""
        activity = super(DetailsView, self).get_object(queryset)
        print(activity.user)
        print(self.request.user)
        if self.request.user != activity.user:
            raise PermissionDenied
        return activity

    def get_context_data(self, **kwargs):
        """Add additional content to the user page"""
        context = super(DetailsView, self).get_context_data(**kwargs)
        if self.object.name is None:
            cancel_link = reverse('delete_activity', args=[self.object.id])
        else:
            cancel_link = reverse('view_activity', args=[self.object.id])
        context['cancel_link'] = cancel_link
        context['units'] = UNIT_SETTING
        return context


class ActivityView(UploadFormMixin, DetailView):
    """Activity view"""
    model = Activity
    template_name = 'activity.html'
    context_object_name = 'activity'

    def get_object(self, queryset=None):
        """Get activity, only allowing owner to see private activities"""
        activity = super().get_object(queryset)
        Helper.verify_private_owner(activity, self.request)
        return activity

    def get_context_data(self, **kwargs):
        """Add additional content to the user page"""
        context = super(ActivityView, self).get_context_data(**kwargs)
        context['val_errors'] = ERRORS
        context['units'] = UNIT_SETTING
        return context


class ActivityTrackView(ActivityView):
    """Activity Track view"""
    model = ActivityTrack
    template_name = 'track.html'
    context_object_name = 'track'
