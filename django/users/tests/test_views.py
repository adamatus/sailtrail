from unittest.mock import patch, sentinel, Mock, MagicMock

from core.views import UploadFormMixin
from users.views import (UserListView, UserView, UserSettingsView,
                         ChangePasswordView)


class TestUserView:

    @patch('users.views.ListView.get')
    @patch('users.views.get_user_model')
    def test_get_adds_user_to_view(self, mock_get_user_model, get_mock):
        # Given a mock that returns a sentinel user
        users_mock = Mock()
        users_mock.objects.get.return_value = sentinel.user
        mock_get_user_model.return_value = users_mock

        get_mock.return_value = sentinel.response

        view = UserView()
        view.kwargs = dict(username=sentinel.username)

        # When getting the view
        response = view.get(sentinel.request)

        # Then the sentinel user is returned, via the mock
        assert view.user == sentinel.user
        users_mock.objects.get.assert_called_with(username=sentinel.username)
        assert response == sentinel.response
        get_mock.assert_called_once_with(sentinel.request)

    @patch('users.views.get_users_activities')
    def test_get_queryset_calls_helper(self, mock_helper):
        # Given a mock that returns a sentinel
        mock_helper.return_value = sentinel.activities

        # and a view user
        view = UserView()
        view.user = sentinel.user
        view.request = Mock(user=sentinel.other)

        # When getting the queryset
        activities = view.get_queryset()

        # Then the sentinel is returned, via the helper
        assert activities == sentinel.activities
        mock_helper.assert_called_once_with(sentinel.user, sentinel.other)

    @patch('users.views.summarize_by_category')
    @patch('users.views.ListView.get_context_data')
    def test_get_context_data_populates_correctly(self, super_mock,
                                                  mock_helper):
        # Given a mock that returns a sentinel summary
        mock_helper.return_value = sentinel.summary
        super_mock.return_value = dict(super=sentinel.super)

        # and a mock queryset that returns a sentinel
        view = UserView()
        view.user = sentinel.user
        view.get_queryset = Mock(return_value=sentinel.activity_query_set)

        # When getting the context data
        context = view.get_context_data()

        # Then the context contains the sentinel summary, via the mock
        assert context['summaries'] == sentinel.summary
        assert context['view_user'] == sentinel.user
        assert context['super'] == sentinel.super
        mock_helper.assert_called_once_with(sentinel.activity_query_set)

    def test_includes_upload_form_mixin(self):
        # Expect the view to have the upload form in the hierarchy
        view = UserView()
        assert isinstance(view, UploadFormMixin)


class TestUserSettingsView:

    @patch('users.views.DetailView.get_context_data')
    def test_get_context_with_no_notify_in_session(self, super_mock):
        super_mock.return_value = dict(super=sentinel.super)

        view = UserSettingsView()
        view.request = Mock(session=dict())

        # When getting the context data
        context = view.get_context_data()

        # Then notify is not in the context
        assert 'notify' not in context
        assert context['super'] == sentinel.super

    @patch('users.views.DetailView.get_context_data')
    def test_get_context_with_notify_in_session(self, super_mock):
        super_mock.return_value = {}
        # Given a request session with a notify value
        view = UserSettingsView()
        view.request = Mock(session=dict(notify=sentinel.notify))

        # When getting the context data
        context = view.get_context_data()

        # Then the notify value is included in the context
        assert context['notify'] == sentinel.notify

        # and the notify value is removed from the session
        assert 'notify' not in view.request.session


class TestChangePasswordView:

    @patch('users.views.reverse')
    def test_get_success_url(self, reverse_mock: MagicMock):
        # Given a mock that returns a sentinel url
        reverse_mock.return_value = sentinel.url

        view = ChangePasswordView()
        view.request = Mock(session=dict())
        view.request.user = Mock(username=sentinel.username)

        # When getting the success url
        url = view.get_success_url()

        # Then the sentinel is return, after the mock is called correctly
        assert url == sentinel.url
        reverse_mock.assert_called_once_with('user_settings',
                                             args=[sentinel.username])


class TestUserListView:

    def test_includes_upload_form_mixin(self):
        # Expect the form to include upload form in hierarchy
        assert isinstance(UserListView(), UploadFormMixin)
