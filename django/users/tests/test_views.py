import unittest
from unittest.mock import patch, sentinel, Mock, MagicMock

from django.test import RequestFactory

from core.views import UploadFormMixin
from users.tests.factories import UserFactory
from users.views import UserListView, UserView, UserSettingsView, \
    ChangePasswordView


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

        assert self.view.user == sentinel.user

        users_mock.objects.get.assert_called_with(username=sentinel.username)

    @patch('users.views.Helper')
    def test_get_queryset_calls_helper(self, mock_helper):
        mock_helper.get_users_activities.return_value = sentinel.activities
        self.view.user = sentinel.user
        activities = self.view.get_queryset()

        assert activities == sentinel.activities

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

        assert context['summaries'] == sentinel.summary

    @patch('users.views.Helper')
    def test_get_context_data_includes_user(self, mock_helper):

        self.view.user = sentinel.user

        context = self.view.get_context_data()

        assert context['view_user'] == sentinel.user

    def test_includes_upload_form_mixin(self):
        assert isinstance(self.view, UploadFormMixin)


class TestUserSettingsView(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.user = UserFactory.stub()
        self.request.session = {}
        self.view = UserSettingsView()
        self.view.object = Mock()
        self.view.request = self.request

    def test_get_context_with_no_notify_in_session(self):
        context = self.view.get_context_data()

        assert 'notify' not in context

    def test_get_context_with_notify_in_session(self):
        self.request.session = dict(notify=sentinel.notify)
        context = self.view.get_context_data()

        assert context['notify'] == sentinel.notify
        assert 'notify' not in self.request.session


class TestChangePasswordView:

    @patch('users.views.reverse')
    def test_get_success_url(self, reverse_mock: MagicMock):
        view = ChangePasswordView()
        view.request = RequestFactory()
        view.request.session = {}
        user_mock = Mock()
        user_mock.username = sentinel.username
        view.request.user = user_mock

        reverse_mock.return_value = sentinel.url

        url = view.get_success_url()
        assert url == sentinel.url
        reverse_mock.assert_called_once_with('user_settings',
                                             args=[sentinel.username])


class TestUserListView:

    def test_includes_upload_form_mixin(self):
        assert isinstance(UserListView(), UploadFormMixin)
