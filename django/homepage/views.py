"""Activity view module"""
from django.views.generic import TemplateView

from api.models import Helper
from core.views import UploadFormMixin
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
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
