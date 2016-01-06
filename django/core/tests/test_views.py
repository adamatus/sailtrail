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
        # Given a dummy view that uses the upload form mixin
        view = self.DummyView()

        # When getting context data
        context = view.get_context_data()

        # Then the upload_form is included in the context
        assert isinstance(context['upload_form'], UploadFileForm)


class TestErrorTemplateView:

    def test_as_error_view_includes_status_code(self):

        class TestErrorView(ErrorTemplateView):
            """Dummy error view to test error view"""
            status_code = 113
            template_name = '400.html'

        # Given a test view rendered as an error view
        view = TestErrorView.as_error_view()

        # and a get request
        request = RequestFactory().get('/dummy')

        # When calling the view on the request
        response = view(request)

        # Then the response includes the status code from the error view
        assert response.status_code == 113
