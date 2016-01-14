import unittest
from unittest.mock import Mock, sentinel, patch, MagicMock

import pytest

from django.core.exceptions import PermissionDenied, SuspiciousOperation

from api.views import WindDirection, JSONResponseMixin, BaseJSONView, \
    ActivityJSONView, TrackJSONView, DeleteActivityView, BaseTrackView, \
    DeleteTrackView, TrimView, UntrimView, TrackJSONMixin


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


class TestJSONResponseMixin(unittest.TestCase):

    def setUp(self):
        # Given an implementation using Mixin
        class TestJSONView(JSONResponseMixin):
            data_field = 'test'
        self.view = TestJSONView()

    def test_get_data_returns_value_in_context_field(self):
        # Given some context data with a 'test' field
        context = dict(test=sentinel.json, other=sentinel.other)

        # When getting data
        data = self.view.get_data(context)

        # Then the test field is returned
        assert data == sentinel.json

    @patch('api.views.JsonResponse')
    def test_render_calls_json_response(self, json_mock: MagicMock):
        # Given some context data
        context = dict(test=sentinel.json)

        # and a mock response
        json_mock.return_value = sentinel.response

        # When rendering the response
        response = self.view.render_to_json_response(context)

        # Then the sentinel response is returned, after mock called
        assert response == sentinel.response
        json_mock.assert_called_once_with(sentinel.json)


class TestBaseJSONView(unittest.TestCase):

    def test_return_json_raises_not_implemented(self):
        # Given a base view
        view = BaseJSONView()

        # When returning json, a not implemented is raised
        with pytest.raises(NotImplementedError):
            view.return_json()

    @patch('api.views.verify_private_owner')
    def test_get_object_returns_the_object_after_verifying(self, verify_mock):
        # Given an implementation with an object to return
        class TestBaseJSONView(BaseJSONView):
            kwargs = dict(pk=1)  # Needed for call to super
            request = Mock()
        view = TestBaseJSONView()

        # and a mock queryset
        queryset = Mock()
        queryset.filter.return_value.get.return_value = sentinel.object

        # When getting the object
        data = view.get_object(queryset=queryset)

        # Then
        assert data == sentinel.object

    def test_render_to_response_returns_result_of_render_to_json(self):
        # Given an implementation with a control render_to_json
        class TestBaseJSONView(BaseJSONView):
            def render_to_json_response(self, context, **response_kwargs):
                assert context == sentinel.context  # check arg passed
                return sentinel.json
        view = TestBaseJSONView()

        # When rendering the view
        response = view.render_to_response(sentinel.context)

        # Then the sentinel is returned
        assert response == sentinel.json

    def test_get_context_data_returns_results_of_return_json(self):
        # Given an implementation with a control return_json

        class TestBaseJSONView(BaseJSONView):
            data_field = 'test'
            object = None  # required for super call

            def return_json(self):
                return sentinel.json

        view = TestBaseJSONView()

        # When getting the context
        context = view.get_context_data()

        # Then the sentinel is returned
        assert context['test'] == sentinel.json


class TestTrackJSONMixin:

    def test_get_trackpoints_raises(self):
        mixin = TrackJSONMixin()

        with pytest.raises(NotImplementedError):
            mixin.get_trackpoints()

    @patch('api.views.make_json_from_trackpoints')
    def test_return_json_returns_helper_call(self, helper_mock: MagicMock):
        # Given a mixin with mock get_trackpoints
        mixin = TrackJSONMixin()
        mixin.get_trackpoints = Mock(return_value=sentinel.tps)

        # and helper mock that returns sentinel json
        helper_mock.return_value = sentinel.json

        # When returning json
        json = mixin.return_json()

        # then the sentinel json is returned
        assert json == sentinel.json
        helper_mock.assert_called_once_with(sentinel.tps)


class TestActivityJSONView:

    def test_get_trackpoints(self):
        trackpoints = Mock()
        trackpoints.get_trackpoints.return_value = sentinel.tps

        class TestView(ActivityJSONView):
            def get_object(self, queryset=None):
                return trackpoints

        view = TestView()

        tps = view.get_trackpoints()

        assert tps == sentinel.tps
        trackpoints.get_trackpoints.assert_called_once_with()


class TestTrackJSONView:

    def test_get_trackpoints(self):
        # Given a test class with mock get_object
        trackpoints = Mock()
        trackpoints.get_trackpoints.return_value.values.return_value = \
            [sentinel.tp1, sentinel.tp2]

        class TestView(TrackJSONView):
            def get_object(self, queryset=None):
                return trackpoints
        view = TestView()

        # When getting the trackpoints
        tps = view.get_trackpoints()

        # Then the correct list is returned, after mock calls
        assert tps == [sentinel.tp1, sentinel.tp2]
        trackpoints.get_trackpoints.assert_called_once_with()
        trackpoints.get_trackpoints.return_value.values.\
            assert_called_once_with('sog', 'lat', 'lon', 'timepoint')


class TestDeleteActivityView:

    def test_get_object_throws_if_not_request_user(self):
        view = DeleteActivityView()
        view.queryset = Mock()
        view.kwargs = dict(pk=1)
        view.request = Mock(user=sentinel.user)

        with pytest.raises(PermissionDenied):
            view.get_object(queryset=Mock())

    def test_get_object_returns_activity_if_users(self):
        # Given a view with fakes to get super call to work
        view = DeleteActivityView()
        view.kwargs = dict(pk=1)
        view.request = Mock(user=sentinel.user)

        # and a mock queryset that will return mock with sentinel
        activity_mock = Mock(user=sentinel.user)
        queryset_mock = Mock()
        queryset_mock.filter.return_value.get.return_value = activity_mock

        # When getting the object
        activity = view.get_object(queryset=queryset_mock)

        # Then the activity is returned
        assert activity == activity_mock

    @patch('api.views.redirect')
    def test_get_deletes_object_and_redirects(self, redirect_mock: MagicMock):

        # Given a view with mock get_object
        view = DeleteActivityView()
        delete_mock = Mock()
        view.get_object = Mock(return_value=delete_mock)

        # and a redirect mock that returns a sentinel
        redirect_mock.return_value = sentinel.response

        # When getting the view
        response = view.get(Mock())

        # Then the response will be a redirect
        assert response == sentinel.response
        redirect_mock.assert_called_once_with('home')

        # and the object will have been deleted
        delete_mock.delete.assert_called_once_with()


class TestBaseTrackView:

    def test_get_object_raises_if_not_correct_user(self):
        view = BaseTrackView()
        view.kwargs = dict(pk=1)
        view.request = Mock(user=sentinel.user)

        # and a mock queryset that will return mock with sentinel
        track_mock = Mock()
        track_mock.activity_id.user = sentinel.other_user
        queryset_mock = Mock()
        queryset_mock.filter.return_value.get.return_value = track_mock

        with pytest.raises(PermissionDenied):
            view.get_object(queryset=queryset_mock)

    def test_get_object_returns_track_if_cur_user(self):
        view = BaseTrackView()
        view.kwargs = dict(pk=1)
        view.request = Mock(user=sentinel.user)

        # and a mock queryset that will return mock with sentinel
        track_mock = Mock()
        track_mock.activity_id.user = sentinel.user
        queryset_mock = Mock()
        queryset_mock.filter.return_value.get.return_value = track_mock

        track = view.get_object(queryset=queryset_mock)

        assert track == track_mock


class TestDeleteTrackView:

    def test_get_raises_if_activity_has_fewer_than_2_tracks(self):
        track = Mock()
        track.activity_id.track.count.return_value = 1
        view = DeleteTrackView()
        view.get_object = Mock(return_value=track)

        with pytest.raises(SuspiciousOperation):
            view.get(Mock())

    @patch('api.views.redirect')
    def test_get_deletes_and_resets_if_more_than_2(self,
                                                   redir_mock: MagicMock):
        # Given a mock track
        track = Mock()
        track.activity_id.track.count.return_value = 2
        track.activity_id.id = sentinel.activity_id

        # and a view with mock get_object that returns track
        view = DeleteTrackView()
        view.get_object = Mock(return_value=track)

        # and a mock redirect
        redir_mock.return_value = sentinel.response

        # When getting the view
        response = view.get(Mock())

        # The mocked response sentinel is returned
        assert response == sentinel.response
        redir_mock.assert_called_once_with('view_activity',
                                           sentinel.activity_id)

        # and the track is reset properly
        track.delete.assert_called_once_with()
        assert track.activity_id.model_distance is None
        assert track.activity_id.model_max_speed is None
        track.activity_id.compute_stats.assert_called_once_with()


class TestTrimView(unittest.TestCase):

    def setUp(self):
        # Given a mock track
        self.track_mock = Mock()
        self.track_mock.activity_id.id = sentinel.id

        # and a view with a mock get_object that returns track
        self.view = TrimView()
        self.view.get_object = Mock(return_value=self.track_mock)

        # and a mock redirect that returns a sentinel response
        patcher = patch('api.views.redirect')
        self.redir_mock = patcher.start()
        self.redir_mock.return_value = sentinel.response
        self.addCleanup(patcher.stop)

    def test_post_trims_and_redirects_to_activity(self):
        # Given setup and a mock request with data
        request = Mock(POST={'trim-start': sentinel.start,
                             'trim-end': sentinel.end})

        # When posting request to view
        response = self.view.post(request)

        # Then sentinel response is returned via correct call to redirect
        assert response == sentinel.response
        self.redir_mock.assert_called_once_with('view_activity', sentinel.id)

        # and track is trimmed with correct data
        self.track_mock.trim.assert_called_once_with(sentinel.start,
                                                     sentinel.end)

    def test_post_trims_and_redirects_to_activity_with_only_start(self):
        # Given setup and a mock request with data
        request = Mock(POST={'trim-start': sentinel.start})

        # When posting request to view
        response = self.view.post(request)

        # Then sentinel response is returned via correct call to redirect
        assert response == sentinel.response
        self.redir_mock.assert_called_once_with('view_activity', sentinel.id)

        # and track is trimmed with correct data
        self.track_mock.trim.assert_called_once_with(sentinel.start, '-1')

    def test_post_trims_and_redirects_to_activity_with_only_end(self):
        # Given setup and a mock request with data
        request = Mock(POST={'trim-end': sentinel.end})

        # When posting request to view
        response = self.view.post(request)

        # Then sentinel response is returned via correct call to redirect
        assert response == sentinel.response
        self.redir_mock.assert_called_once_with('view_activity', sentinel.id)

        # and track is trimmed with correct data
        self.track_mock.trim.assert_called_once_with('-1', sentinel.end)


class TestUntrimView:

    @patch('api.views.redirect')
    def test_get_untrims_object(self, redir_mock: MagicMock):
        # Given a mock track
        track = Mock()
        track.activity_id.id = sentinel.activity_id

        # and a view with mock get_object that returns track
        view = UntrimView()
        view.get_object = Mock(return_value=track)

        # and mock redirect that returns sentinel
        redir_mock.return_value = sentinel.response

        # When getting the view
        response = view.get(None)

        # Then sentinel is returned after correct redirect call
        assert response == sentinel.response
        redir_mock.assert_called_once_with('view_activity',
                                           sentinel.activity_id)

        # and track had trim reset
        track.reset_trim.assert_called_once_with()
