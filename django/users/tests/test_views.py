import unittest
from unittest.mock import patch, sentinel

from django.test import RequestFactory

from core.forms import UploadFileForm
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

    @patch('users.views.summarize_by_category')
    @patch('users.views.get_users_activities')
    def test_get_context_data_populates_activities(self, mock_get,
                                                   mock_summarize):

        mock_get.return_value = sentinel.activity_query_set
        mock_summarize.return_value = sentinel.summary

        context = self.view.get_context_data()

        mock_get.assert_called_once_with(self.user, self.user)
        mock_summarize.assert_called_once_with(sentinel.activity_query_set)

        self.assertEqual(context['activities'], sentinel.activity_query_set)
        self.assertEqual(context['summaries'], sentinel.summary)

    def test_get_context_data_adds_form(self):
        context = self.view.get_context_data()
        self.assertIsInstance(context['form'], UploadFileForm)


class TestUserListView(unittest.TestCase):

    def test_context_data_adds_form(self):
        view = UserListView()
        view.object_list = []

        context = view.get_context_data()

        self.assertIsInstance(context['form'], UploadFileForm)
