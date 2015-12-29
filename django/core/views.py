"""Shared view mixins"""

from .forms import UploadFileForm


class UploadFormMixin(object):
    """A mixin that adds the upload form to the context"""

    def get_context_data(self, **kwargs):
        """Add additional data to user list context"""
        context = super(UploadFormMixin, self).get_context_data(**kwargs)
        context['upload_form'] = UploadFileForm()
        return context
