"""Activity view module"""
from django.db.models import QuerySet
from django.views.generic import ListView

from api.models import Helper, Activity
from core.views import UploadFormMixin
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)

ERRORS = dict(no_file=ERROR_NO_UPLOAD_FILE_SELECTED,
              bad_file_type=ERROR_UNSUPPORTED_FILE_TYPE)


class HomePageView(UploadFormMixin, ListView):
    """Handle logged-in user home page"""
    model = Activity
    template_name = 'home.html'
    context_object_name = 'activities'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        """Overridden queryset to return activities

        Includes current users private activities"""
        return Helper.get_activities(self.request.user)

    def get_context_data(self, **kwargs) -> dict:
        """Update the context with addition homepage data"""
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['leaders'] = Helper.get_leaders()
        context['val_errors'] = ERRORS
        return context
