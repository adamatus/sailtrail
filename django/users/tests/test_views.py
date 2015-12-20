import unittest
from unittest.mock import patch, sentinel

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
        view.object = self.user
        self.view = view

    @patch('users.views.Helper')
    def test_get_context_data_populates_activities(self, mock_helper):

        mock_helper.get_users_activities.return_value = \
            sentinel.activity_query_set
        mock_helper.summarize_by_category.return_value = sentinel.summary

        context = self.view.get_context_data()

        mock_helper.get_users_activities.assert_called_once_with(self.user,
                                                                 self.user)
        mock_helper.summarize_by_category.assert_called_once_with(
            sentinel.activity_query_set)

        self.assertEqual(context['activities'], sentinel.activity_query_set)
        self.assertEqual(context['summaries'], sentinel.summary)

    def test_includes_upload_form_mixin(self):
        self.assertIsInstance(self.view, UploadFormMixin)


class TestUserListView(unittest.TestCase):

    def test_includes_upload_form_mixin(self):
        self.assertIsInstance(UserListView(), UploadFormMixin)
