import unittest

from django.views.generic import TemplateView

from core.forms import UploadFileForm
from core.views import UploadFormMixin


class TestUploadFormMixing(unittest.TestCase):

    class DummyView(UploadFormMixin, TemplateView):
        """Dummy view to test mixin"""
        template_name = 'dummy_template.html'

    def test_context_data_adds_form(self):
        view = self.DummyView()
        context = view.get_context_data()

        self.assertIsInstance(context['upload_form'], UploadFileForm)
