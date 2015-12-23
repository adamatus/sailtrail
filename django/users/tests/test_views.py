import unittest
from unittest.mock import patch, sentinel, Mock

from django.test import RequestFactory

from core.views import UploadFormMixin
from users.tests.factories import UserFactory
from users.views import UserListView, UserView


class TestUserView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        view = UserView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('users.views.Helper')
    def test_get_context_data_populates_activities(self, mock_helper):

        mock_helper.summarize_by_category.return_value = sentinel.summary

        self.view.get_queryset = Mock()
        self.view.get_queryset.return_value = sentinel.activity_query_set

        context = self.view.get_context_data()

        mock_helper.summarize_by_category.assert_called_once_with(
            sentinel.activity_query_set)

        self.assertEqual(context['summaries'], sentinel.summary)

    @patch('users.views.Helper')
    def test_get_context_data_includes_user(self, mock_helper):

        self.view.user = sentinel.user

        context = self.view.get_context_data()

        self.assertEqual(context['view_user'], sentinel.user)

    def test_includes_upload_form_mixin(self):
        self.assertIsInstance(self.view, UploadFormMixin)


class TestUserListView(unittest.TestCase):

    def test_includes_upload_form_mixin(self):
        self.assertIsInstance(UserListView(), UploadFormMixin)
