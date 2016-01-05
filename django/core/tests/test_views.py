import unittest

from django.test import RequestFactory
from django.views.generic import TemplateView

from core.forms import UploadFileForm
from core.views import UploadFormMixin, ErrorTemplateView


class TestUploadFormMixing(unittest.TestCase):

    class DummyView(UploadFormMixin, TemplateView):
        """Dummy view to test mixin"""
        template_name = 'dummy_template.html'

    def test_context_data_adds_form(self):
        view = self.DummyView()
        context = view.get_context_data()

        assert isinstance(context['upload_form'], UploadFileForm)


class TestErrorTemplateView:

    def test_as_error_view_includes_status_code(self):

        class TestErrorView(ErrorTemplateView):
            status_code = 113
            template_name = '400.html'

        view = TestErrorView.as_error_view()

        request = RequestFactory(method="GET")
        request.method = 'GET'
        response = view(request)

        assert response.status_code == 113
