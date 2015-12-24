import unittest
from unittest.mock import patch, sentinel, Mock

from django.test import RequestFactory

from core.views import UploadFormMixin
from users.tests.factories import UserFactory
from users.views import UserListView, UserView


class TestUserView(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.user = UserFactory.stub()
        view = UserView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('users.views.get_user_model')
    def test_get_adds_user_to_view(self, mock_get_user_model):
        users_mock = Mock()
        users_mock.objects.get.return_value = sentinel.user
        mock_get_user_model.return_value = users_mock

        self.view.get_context_data = Mock()
        self.view.get_queryset = Mock()
        self.view.kwargs = dict(username=sentinel.username)

        self.view.get(self.request)

        self.assertEqual(self.view.user, sentinel.user)

        users_mock.objects.get.assert_called_with(username=sentinel.username)

    @patch('users.views.Helper')
    def test_get_queryset_calls_helper(self, mock_helper):
        mock_helper.get_users_activities.return_value = sentinel.activities
        self.view.user = sentinel.user
        activities = self.view.get_queryset()

        self.assertEqual(activities, sentinel.activities)

        user = self.request.user
        mock_helper.get_users_activities.assert_called_once_with(sentinel.user,
                                                                 user)

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
