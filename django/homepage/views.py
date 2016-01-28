"""Activity view module"""
from django.db.models import QuerySet
from django.views.generic import ListView

from api.helper import get_leaders, get_activities_for_user
from api.models import Activity
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
        return get_activities_for_user(self.request.user)

    def get_context_data(self, **kwargs) -> dict:
        """Update the context with addition homepage data"""
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['leaders'] = get_leaders()
        context['val_errors'] = ERRORS
        return context
