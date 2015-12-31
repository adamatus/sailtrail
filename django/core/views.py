"""Shared view mixins"""
from django.views.generic import TemplateView

from .forms import UploadFileForm


class UploadFormMixin(object):
    """A mixin that adds the upload form to the context"""

    def get_context_data(self, **kwargs) -> dict:
        """Add additional data to user list context"""
        context = super(UploadFormMixin, self).get_context_data(**kwargs)
        context['upload_form'] = UploadFileForm()
        return context


class ErrorTemplateView(UploadFormMixin, TemplateView):
    """Base template view for error pages"""
    @classmethod
    def as_error_view(cls):
        """Render the view"""
        class_view = cls.as_view()

        def view(request):
            """Method to render the view"""
            response = class_view(request)
            response.render()
            response.status_code = cls.status_code
            return response
        return view


class BadRequestView(ErrorTemplateView):
    """Standard 400 page view"""
    template_name = "400.html"
    status_code = 400


class PermissionDeniedView(ErrorTemplateView):
    """Standard 403 page view"""
    template_name = "403.html"
    status_code = 403


class NotFoundView(ErrorTemplateView):
    """Standard 404 page view"""
    template_name = "404.html"
    status_code = 404


class InternalServerErrorView(ErrorTemplateView):
    """Standard 500 page view"""
    template_name = "500.html"
    status_code = 500
