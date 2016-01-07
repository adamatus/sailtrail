import unittest
from unittest.mock import Mock, sentinel, patch

import pytest

from django.core.exceptions import PermissionDenied

from api.views import WindDirection


class TestWindDirection(unittest.TestCase):

    def setUp(self):
        patcher = patch('api.views.HttpResponse')
        self.mock_http = patcher.start()
        self.addCleanup(patcher.stop)

        self.user = sentinel.user
        self.request = Mock(user=self.user)

    def build_mock_class(self, activity):
        """ Helper method to return a class that mocks out the super's
        get_object to return the provided activity mock
        """
        class MockedGetObject(object):
            def get_object(self):
                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        return MockedWindDirection

    @patch('api.views.json')
    def test_get_returns_existing_wind_direction(self,
                                                 mock_json):
        # Given a mock public activity for a different user
        activity = Mock(user=sentinel.other_user, wind_direction="10.0",
                        private=False)

        # and mocked view who's super returns that activity
        view = self.build_mock_class(activity)()
        view.kwargs = dict(pk=1)

        # and mocked helpers that return sentinels
        mock_json.dumps.return_value = sentinel.json_data
        self.mock_http.return_value = sentinel.http_response

        # When getting the view
        response = view.get(self.request)

        # Then the sentinel response is returned, after correct helper calls
        assert response == sentinel.http_response
        mock_json.dumps.assert_called_once_with(dict(wind_direction="10.0"))
        self.mock_http.assert_called_once_with(sentinel.json_data,
                                               content_type="application/json")

    def test_get_returns_if_private_and_cur_user(self):
        # Given a mock activity for the current user
        activity = Mock(user=self.user, wind_direction="10.0",
                        private=False)

        # and mocked view who's super returns that activity
        view = self.build_mock_class(activity)()
        view.kwargs = dict(pk=1)

        # and mocked helpers that return sentinels
        self.mock_http.return_value = sentinel.http_response

        # When getting the view
        response = view.get(self.request)

        # Then the sentinel response is returned, after correct helper calls
        assert response == sentinel.http_response
        assert self.mock_http.called is True

    def test_get_raises_permission_denied_if_wrong_user_and_private(self):
        # Given a mock private activity for a different user
        activity = Mock(user=sentinel.other_user, wind_direction="10.0",
                        private=True)

        # and mocked view who's super returns that activity
        view = self.build_mock_class(activity)()
        view.kwargs = dict(pk=1)

        # and mocked helper that return a sentinel
        self.mock_http.return_value = sentinel.http_response

        # When getting the view, Then a permission denied is raised
        with pytest.raises(PermissionDenied):
            view.get(self.request)

    def test_post_throws_if_not_current_user(self):
        # Given a mock private activity for a different user
        activity = Mock(user=sentinel.other_user, wind_direction="10.0",
                        private=True)

        # and mocked view who's super returns that activity
        view = self.build_mock_class(activity)()
        view.kwargs = dict(pk=1)

        # When posting to the view, Then a permission denied is raised
        with pytest.raises(PermissionDenied):
            view.post(self.request)

    def test_post_saves_wind_dir(self):
        # Given a mock private activity for the current user
        activity = Mock(user=self.user, wind_direction="10.0",
                        private=True)

        # and mocked view who's super returns that activity
        view = self.build_mock_class(activity)()
        view.kwargs = dict(pk=1)
        view.get = Mock()

        # When posting to the view
        self.request.POST = dict(wind_direction="20.0")
        view.post(self.request)

        # Then the wind_direction is updated, and helpers called correctly
        assert activity.wind_direction == "20.0"
        activity.save.assert_called_once_with()
        view.get.assert_called_once_with(self.request)
