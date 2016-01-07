import unittest
from unittest.mock import patch, sentinel, Mock, MagicMock

from core.views import UploadFormMixin
from users.views import (UserListView, UserView, UserSettingsView,
                         ChangePasswordView)


class TestUserView(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.user = sentinel.user
        view = UserView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('users.views.get_user_model')
    def test_get_adds_user_to_view(self, mock_get_user_model):
        # Given a mock that returns a sentinel user
        users_mock = Mock()
        users_mock.objects.get.return_value = sentinel.user
        mock_get_user_model.return_value = users_mock

        # and view mocks that result in the user getting returned
        self.view.get_context_data = Mock()
        self.view.get_queryset = Mock()
        self.view.kwargs = dict(username=sentinel.username)

        # When getting the view
        self.view.get(self.request)

        # Then the sentinel user is returned, via the mock
        assert self.view.user == sentinel.user
        users_mock.objects.get.assert_called_with(username=sentinel.username)

    @patch('users.views.get_users_activities')
    def test_get_queryset_calls_helper(self, mock_helper):
        # Given a mock that returns a sentinel
        mock_helper.return_value = sentinel.activities

        # and a view user
        self.view.user = sentinel.user

        # When getting the queryset
        activities = self.view.get_queryset()

        # Then the sentinel is returned, via the helper
        assert activities == sentinel.activities
        mock_helper.assert_called_once_with(sentinel.user, self.request.user)

    @patch('users.views.summarize_by_category')
    def test_get_context_data_populates_activities(self, mock_helper):
        # Given a mock that returns a sentinel summary
        mock_helper.return_value = sentinel.summary

        # and a mock queryset that returns a sentinel
        self.view.get_queryset = Mock(return_value=sentinel.activity_query_set)

        # When getting the context data
        context = self.view.get_context_data()

        # Then the context contains the sentinel summary, via the mock
        assert context['summaries'] == sentinel.summary
        mock_helper.assert_called_once_with(sentinel.activity_query_set)

    @patch('users.views.get_users_activities')
    @patch('users.views.summarize_by_category')
    def test_get_context_data_includes_user(self, unused_mock, unused_mock2):
        # Given a sentinel view user
        self.view.user = sentinel.user

        # When getting the context data
        context = self.view.get_context_data()

        # Then the context contains the view user
        assert context['view_user'] == sentinel.user

    def test_includes_upload_form_mixin(self):
        # Expect the view to have the upload form in the hierarchy
        assert isinstance(self.view, UploadFormMixin)


class TestUserSettingsView(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.user = sentinel.user
        self.request.session = {}
        self.view = UserSettingsView()
        self.view.object = Mock()
        self.view.request = self.request

    def test_get_context_with_no_notify_in_session(self):
        # When getting the context data
        context = self.view.get_context_data()

        # Then notify is not in the context
        assert 'notify' not in context

    def test_get_context_with_notify_in_session(self):
        # Given a request session with a notify value
        self.request.session = dict(notify=sentinel.notify)

        # When getting the context data
        context = self.view.get_context_data()

        # Then the notify value is included in the context
        assert context['notify'] == sentinel.notify

        # and the notify value is removed from the session
        assert 'notify' not in self.request.session


class TestChangePasswordView(unittest.TestCase):

    def setUp(self):
        view = ChangePasswordView()
        view.request = Mock()
        view.request.session = {}
        self.view = view

    @patch('users.views.reverse')
    def test_get_success_url(self, reverse_mock: MagicMock):
        # Given a mock that returns a sentinel url
        reverse_mock.return_value = sentinel.url

        # and a request with mock user
        self.view.request.user = Mock(username=sentinel.username)

        # When getting the success url
        url = self.view.get_success_url()

        # Then the sentinel is return, after the mock is called correctly
        assert url == sentinel.url
        reverse_mock.assert_called_once_with('user_settings',
                                             args=[sentinel.username])


class TestUserListView:

    def test_includes_upload_form_mixin(self):
        # Expect the form to include upload form in hierarchy
        assert isinstance(UserListView(), UploadFormMixin)
