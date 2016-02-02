from datetime import datetime
from unittest.mock import patch, sentinel, Mock

import pytest
import pytz
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.core.urlresolvers import reverse

from activities.views import (UploadView, UploadTrackView,
                              DetailsView, ActivityTrackView, ActivityView,
                              ActivityTrackDownloadView, ActivityTrackTrimView)


class TestUploadView:

    @patch('activities.views.UploadFileForm', spec=True)
    def test_post_raises_suspicious_operation_on_bad_form(self, up_mock):
        # Given an upload file form mock that is marked as invalid
        form = Mock()
        form.is_valid.return_value = False
        up_mock.return_value = form

        view = UploadView()

        # When posting to the view, Then a suspicious operation will be raised
        with pytest.raises(SuspiciousOperation):
            view.post(Mock(POST=sentinel.POST, FILES=sentinel.FILES))

        # and the upload form will be created with the correct request data
        up_mock.assert_called_with(sentinel.POST,
                                   sentinel.FILES)

    @patch('activities.views.redirect')
    @patch('activities.views.create_new_activity_for_user')
    @patch('activities.views.UploadFileForm')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            up_mock,
                                                            create_mock,
                                                            redir_mock):
        # Given an upload file form mock that is marked as valid and has files
        form = Mock(cleaned_data=dict(upfile=[sentinel.file1,
                                              sentinel.file2]))
        form.is_valid.return_value = True
        up_mock.return_value = form

        # and a create activity mock that returns a mock new activity
        new_activity_mock = Mock(id=sentinel.id)
        create_mock.return_value = new_activity_mock

        view = UploadView()

        redir_mock.return_value = sentinel.response

        # When posting the request to the view
        response = view.post(Mock(POST=sentinel.POST,
                                  FILES=sentinel.FILES,
                                  user=sentinel.user))

        # Then the helper will be called with the request user
        create_mock.assert_called_with(user=sentinel.user)

        # and the files will be added to the new activity
        new_activity_mock.add_track.assert_any_call(sentinel.file1)
        new_activity_mock.add_track.assert_any_call(sentinel.file2)

        # and the correct redirect response will be returned
        redir_mock.assert_called_with('details', sentinel.id)
        assert response == sentinel.response


class TestUploadTrackView:

    @patch('activities.views.get_activity_by_id')
    def test_post_raises_permission_denied_if_not_owner(self, get_mock):
        # Given a mock that returns a mock activity with different user
        get_mock.return_value = Mock(user=sentinel.other)

        view = UploadTrackView()

        # When posting to the view, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            view.post(Mock(user=sentinel.user), sentinel.activity_id)

        # and the mock will be called with the activity id
        get_mock.assert_called_with(sentinel.activity_id)

    @patch('activities.views.UploadFileForm')
    @patch('activities.views.get_activity_by_id')
    def test_post_raises_suspicious_operation_on_bad_form(self,
                                                          get_mock,
                                                          up_mock):
        # Given a mock that returns a mock activity for current user
        get_mock.return_value = Mock(user=sentinel.user)

        # and an upload form mock that is marked as invalid
        form = Mock()
        form.is_valid.return_value = False
        up_mock.return_value = form

        view = UploadTrackView()

        # When posting to the view, Then a suspicious operation will be raised
        with pytest.raises(SuspiciousOperation):
            view.post(Mock(user=sentinel.user,
                           POST=sentinel.POST,
                           FILES=sentinel.FILES),
                      sentinel.activity_id)

        # and the upload form will be called with the request data
        up_mock.assert_called_with(sentinel.POST, sentinel.FILES)

    @patch('activities.views.redirect')
    @patch('activities.views.UploadFileForm')
    @patch('activities.views.get_activity_by_id')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            get_mock,
                                                            up_mock,
                                                            redir_mock):
        # Given a get_activity mock that returns a mock activity
        found_activity = Mock(user=sentinel.user, id=sentinel.id)
        get_mock.return_value = found_activity

        # and an upload form mock that is valid and has files
        form = Mock(cleaned_data=dict(upfile=[sentinel.file1,
                                              sentinel.file2]))
        form.is_valid.return_value = True
        up_mock.return_value = form

        redir_mock.return_value = sentinel.response

        view = UploadTrackView()

        # When positing to the view
        response = view.post(Mock(user=sentinel.user,
                                  FILES=sentinel.FILES,
                                  POST=sentinel.POST),
                             sentinel.activity_id)

        # Then the files will be added as tracks to the activity
        found_activity.add_track.assert_any_call(sentinel.file1)
        found_activity.add_track.assert_any_call(sentinel.file2)

        # and the response will be the redirected response
        redir_mock.assert_called_with('view_activity', pk=sentinel.id)
        assert response == sentinel.response


class TestDetailsView:

    @patch('activities.views.UpdateView.get_object')
    def test_get_object_returns_activity_if_current_user(self, mock):
        # Given a mocked queryset that will return a mock activity for
        # the current user
        mock.return_value = Mock(user=sentinel.user)

        view = DetailsView()
        view.request = Mock(user=sentinel.user)

        # When getting the object
        activity = view.get_object()

        # Then the mock activity will be returned
        assert activity == mock.return_value

    @patch('activities.views.UpdateView.get_object')
    def test_get_object_raises_permission_error_if_not_current_user(
        self,
        mock
    ):
        # Given a mocked queryset that will return a mock activity for
        # a different user
        mock.return_value = Mock(user=sentinel.other)

        view = DetailsView()
        view.request = Mock(user=sentinel.user)

        # When getting the object, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            view.get_object()

    @patch('activities.views.UpdateView.get_context_data')
    def test_get_context_adds_delete_cancel_link(self, mock):
        # Given a mock object in the view with no name
        view = DetailsView()
        view.object = Mock(id=1)
        view.object.name = None

        mock.return_value = dict(super=sentinel.super)

        # and a known delete link
        link = reverse('delete_activity', args=[1])

        # When getting the context data
        context = view.get_context_data()

        # Then the delete link will be added to the context
        assert context['cancel_link'] == link
        assert context['super'] == sentinel.super

    @patch('activities.views.UpdateView.get_context_data')
    def test_get_context_adds_view_cancel_link(self, mock):
        # Given a mock object in the view with an existing name
        view = DetailsView()
        view.object = Mock(id=1)
        view.object.name = 'Something'

        mock.return_value = {}

        # and a known cancel link
        link = reverse('view_activity', args=[1])

        # When getting the context data
        context = view.get_context_data()

        # Then the delete link will be added to the context
        assert context['cancel_link'] == link


class TestActivityView:

    @patch('activities.views.verify_private_owner')
    @patch('activities.views.DetailView.get_object')
    def test_get_object_returns_activity_after_verify(self, get_mock,
                                                      verify_mock):
        # Given a mock parent that returns a mock activity for current user
        view = ActivityView()
        view.request = sentinel.req

        get_mock.return_value = sentinel.activity

        # When getting the object
        activity = view.get_object()

        # Then the mock activity is returned and helper called
        assert activity == sentinel.activity
        verify_mock.assert_called_with(sentinel.activity, sentinel.req)

    @patch('activities.views.DetailView.get_context_data')
    def test_get_context_adds_units_and_errors(self, get_mock):
        view = ActivityView()
        get_mock.return_value = dict(super=sentinel.super)

        # When getting the context data
        context = view.get_context_data()

        # Then the val_errors and units fields are included
        assert context['val_errors'] is not None
        assert context['units'] is not None
        assert context['super'] == sentinel.super


class TestActivityTrackView:

    @patch('activities.views.DetailView.get_queryset')
    def test_get_queryset_calls_parent_and_selects_related(self, detail_mock):
        queryset = Mock()
        queryset.select_related.return_value = sentinel.queryset

        detail_mock.return_value = queryset

        view = ActivityTrackView()

        result = view.get_queryset()
        assert result == sentinel.queryset
        queryset.select_related.assert_called_once_with('activity')

    @patch('activities.views.DetailView.get_object')
    def test_get_object_returns_track_if_current_user(self, get_mock):
        # Given a mock parent that returns a mock track for current user
        mock_track = Mock()
        mock_track.activity.user = sentinel.user
        get_mock.return_value = mock_track

        view = ActivityTrackView()
        view.request = Mock(user=sentinel.user)

        # When getting the object
        track = view.get_object()

        # Then the mock track will be returned
        assert track == mock_track

    @patch('activities.views.DetailView.get_object')
    def test_get_object_raised_permission_denied_if_not_owner(self,
                                                              get_mock):
        # Given a mock parent that returns a mock track for another user
        mock_track = Mock()
        mock_track.activity.user = sentinel.other
        get_mock.return_value = mock_track

        view = ActivityTrackView()
        view.request = Mock(user=sentinel.user)

        # When getting the object, Then permission denied will be raised
        with pytest.raises(PermissionDenied):
            view.get_object()

    @patch('activities.views.DetailView.get_context_data')
    def test_get_context_data_returns_correct_context_data(self, get_mock):
        # Given a mock track with activity with track count of 1
        view = ActivityTrackView()
        view.object = Mock()
        view.object.activity.tracks.count.return_value = 1

        get_mock.return_value = dict(super=sentinel.super)

        # When getting the context data
        context = view.get_context_data()

        # Then the context indicates that this is the last track
        assert context['last_track'] is True
        assert context['val_errors'] is not None
        assert context['units'] is not None
        assert context['super'] == sentinel.super

    @patch('activities.views.DetailView.get_context_data')
    def test_get_context_data_returns_correct_context_data_not_last(self,
                                                                    get_mock):
        # Given a mock track with activity with track count above 1
        view = ActivityTrackView()
        view.object = Mock()
        view.object.activity.tracks.count.return_value = 2

        get_mock.return_value = {}

        # When getting the context data
        context = view.get_context_data()

        # Then the context indicates that this is not the last track
        assert context['last_track'] is False

    @patch('activities.views.DetailView.get_context_data')
    def test_get_context_data_returns_extra_context_data(self, get_mock):
        # When getting the context data
        view = ActivityTrackView()
        view.object = Mock()

        get_mock.return_value = {}

        context = view.get_context_data()

        # Then the val_errors and units fields are included
        assert context['val_errors'] is not None
        assert context['units'] is not None


class TestActivityTrackTrimView:

    @patch('activities.views.ActivityTrackView.get_context_data')
    def test_get_context_calls_parent_and_adds_times(self, super_mock):
        super_mock.return_value = dict(super=sentinel.super)

        track = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2016, 1, 1, tzinfo=pytz.UTC)

        view = ActivityTrackTrimView()
        view.get_object = Mock(return_value=track)

        context = view.get_context_data()
        assert context['super'] == sentinel.super
        assert context['start_time'] == "2015-01-01T00:00:00+0000"
        assert context['end_time'] == "2016-01-01T00:00:00+0000"


class TestActivityTrackDownloadView:

    def test_get_raises_permission_denied_on_bad_user(self):
        # Given a request with another user
        view = ActivityTrackDownloadView()

        mock_track = Mock()
        mock_track.activity.user = sentinel.user
        view.get_object = Mock(return_value=mock_track)

        # When getting the view, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            view.get(Mock(user=sentinel.other))

    def test_get_returns_response_with_file(self):
        view = ActivityTrackDownloadView()

        mock_track = Mock()
        mock_track.activity.user = sentinel.user
        mock_track.original_file.file.name = 'Something/file.gpx'
        view.get_object = Mock(return_value=mock_track)

        # When getting the view as the current user
        response = view.get(Mock(user=sentinel.user))

        # Then the response will contain the file name in the header
        assert 'file.gpx' in response['Content-Disposition']
        assert 'Something/' not in response['Content-Disposition']
