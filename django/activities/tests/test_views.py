import unittest
from unittest.mock import patch, sentinel, Mock

import pytest
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpRequest

from activities.views import (UploadView, UploadTrackView,
                              DetailsView, ActivityTrackView, ActivityView,
                              ActivityTrackDownloadView)
from users.tests.factories import UserFactory


class ViewMockMixin:

    def setUp(self):
        """Stub user and request by that user"""
        self.user = UserFactory.stub()
        self.request = Mock(spec=HttpRequest)  # type: HttpRequest
        self.request.user = self.user

    @staticmethod
    def get_mock_queryset_that_returns_mock_object(mock: Mock) -> Mock:
        """Mocks the steps necessary to get an object in a DetailView

        This takes care of the call to super() to get the object from
        within any class views that have the SingleObjectMixin in them"""
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock

        return mock_queryset

    def setup_view(self, clazz):
        """Create a view, given a class, and set data required for view super
        classes to look it up"""
        view = clazz()
        view.request = self.request
        view.object = Mock()
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        return view


class TestUploadView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestUploadView, self).setUp()

        self.request.POST = sentinel.POST
        self.request.FILES = sentinel.FILES
        self.view = UploadView()

        patcher = patch('activities.views.UploadFileForm', spec=True)
        self.upload_form_mock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher2 = patch('activities.views.create_new_activity_for_user',
                         spec=True)
        self.helper_mock = patcher2.start()
        self.addCleanup(patcher2.stop)

        patcher3 = patch('activities.views.redirect', spec=True,
                         return_value=sentinel.response)
        self.redirect_mock = patcher3.start()
        self.addCleanup(patcher3.stop)

    def test_post_raises_suspicious_operation_on_bad_form(self):
        # Given an upload file form mock that is marked as invalid
        form = Mock()
        form.is_valid.return_value = False
        self.upload_form_mock.return_value = form

        # When posting to the view, Then a suspicious operation will be raised
        with pytest.raises(SuspiciousOperation):
            self.view.post(self.request)

        # and the upload form will be created with the correct request data
        self.upload_form_mock.assert_called_with(sentinel.POST,
                                                 sentinel.FILES)

    def test_post_creates_track_for_each_file_and_redirects(self):
        # Given an upload file form mock that is marked as valid and has files
        form = Mock(cleaned_data=dict(upfile=[sentinel.file1,
                                              sentinel.file2]))
        form.is_valid.return_value = True
        self.upload_form_mock.return_value = form

        # and a create activity mock that returns a mock new activity
        new_activity_mock = Mock(id=sentinel.id)
        self.helper_mock.return_value = new_activity_mock

        # When posting the request to the view
        response = self.view.post(self.request)

        # Then the helper will be called with the request user
        self.helper_mock.assert_called_with(user=self.request.user)

        # and the files will be added to the new activity
        new_activity_mock.add_track.assert_any_call(sentinel.file1)
        new_activity_mock.add_track.assert_any_call(sentinel.file2)

        # and the correct redirect response will be returned
        self.redirect_mock.assert_called_with('details', sentinel.id)
        assert response == sentinel.response


class TestUploadTrackView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestUploadTrackView, self).setUp()

        self.request.POST = sentinel.POST
        self.request.FILES = sentinel.FILES
        self.view = UploadTrackView()

        patcher = patch('activities.views.get_activity_by_id', spec=True)
        self.get_activity_mock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher2 = patch('activities.views.UploadFileForm', spec=True)
        self.upload_form_mock = patcher2.start()
        self.addCleanup(patcher2.stop)

        patcher3 = patch('activities.views.redirect', spec=True,
                         return_value=sentinel.response)
        self.redirect_mock = patcher3.start()
        self.addCleanup(patcher3.stop)

    def test_post_raises_permission_denied_if_not_owner(self):
        # Given a mock that returns a mock activity with different user
        self.get_activity_mock.return_value = Mock(user=UserFactory.stub())

        # When posting to the view, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            self.view.post(self.request, sentinel.activity_id)

        # and the mock will be called with the activity id
        self.get_activity_mock.assert_called_with(sentinel.activity_id)

    def test_post_raises_suspicious_operation_on_bad_form(self):
        # Given a mock that returns a mock activity for current user
        self.get_activity_mock.return_value = Mock(user=self.user)

        # and an upload form mock that is marked as invalid
        form = Mock()
        form.is_valid.return_value = False
        self.upload_form_mock.return_value = form

        # When posting to the view, Then a suspicious operation will be raised
        with pytest.raises(SuspiciousOperation):
            self.view.post(self.request, sentinel.activity_id)

        # and the upload form will be called with the request data
        self.upload_form_mock.assert_called_with(sentinel.POST,
                                                 sentinel.FILES)

    def test_post_creates_track_for_each_file_and_redirects(self):
        # Given a get_activity mock that returns a mock activity
        found_activity = Mock(user=self.user, id=sentinel.id)
        self.get_activity_mock.return_value = found_activity

        # and an upload form mock that is valid and has files
        form = Mock(cleaned_data=dict(upfile=[sentinel.file1,
                                              sentinel.file2]))
        form.is_valid.return_value = True
        self.upload_form_mock.return_value = form

        # When positing to the view
        response = self.view.post(self.request, sentinel.activity_id)

        # Then the files will be added as tracks to the activity
        found_activity.add_track.assert_any_call(sentinel.file1)
        found_activity.add_track.assert_any_call(sentinel.file2)

        # and the response will be the redirected response
        self.redirect_mock.assert_called_with('view_activity', pk=sentinel.id)
        assert response == sentinel.response


class TestDetailsView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestDetailsView, self).setUp()

        self.view = self.setup_view(DetailsView)

    def test_get_object_returns_activity_if_current_user(self):
        # Given a mocked queryset that will return a mock activity for
        # the current user
        mock_activity = Mock(user=self.user)
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_activity)

        # When getting the object
        activity = self.view.get_object(queryset=mock_queryset)

        # Then the mock activity will be returned
        assert activity == mock_activity

    def test_get_object_raises_permission_error_if_not_current_user(self):
        # Given a mocked queryset that will return a mock activity for
        # a different user
        mock_activity = Mock(user=UserFactory.stub())
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_activity)

        # When getting the object, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

    def test_get_context_adds_delete_cancel_link(self):
        # Given a mock object in the view with no name
        self.view.object.id = 1
        self.view.object.name = None

        # and a known delete link
        link = reverse('delete_activity', args=[1])

        # When getting the context data
        context = self.view.get_context_data()

        # Then the delete link will be added to the context
        assert context['cancel_link'] == link

    def test_get_context_adds_view_cancel_link(self):
        # Given a mock object in the view with an existing name
        self.view.object.id = 1
        self.view.object.name = 'Something'

        # and a known cancel link
        link = reverse('view_activity', args=[1])

        # When getting the context data
        context = self.view.get_context_data()

        # Then the delete link will be added to the context
        assert context['cancel_link'] == link


class TestActivityView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestActivityView, self).setUp()

        self.view = self.setup_view(ActivityView)

        patcher = patch('activities.views.verify_private_owner', spec=True)
        self.helper = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_object_returns_activity(self):
        # Given a mock parent that returns a mock activity for current user
        mock_activity = Mock(user=self.user)
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_activity)

        # When getting the object
        activity = self.view.get_object(queryset=mock_queryset)

        # Then the mock activity is returned and helper called
        assert activity == mock_activity
        self.helper.assert_called_with(mock_activity, self.request)

    def test_get_object_raises_permission_denied(self):
        # Given a mock parent that returns a mock activity for current user
        mock_activity = Mock(user=self.user)
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_activity)

        # and a helper that raised permission denied when called
        self.helper.side_effect = PermissionDenied

        # When getting the object, Then the exception is passed on
        with pytest.raises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

        # and the helper will have been called
        self.helper.assert_called_with(mock_activity, self.request)

    def test_get_context_adds_units_and_errors(self):
        # When getting the context data
        context = self.view.get_context_data()

        # Then the val_errors and units fields are included
        assert context['val_errors'] is not None
        assert context['units'] is not None


class TestActivityTrackView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestActivityTrackView, self).setUp()

        self.view = self.setup_view(ActivityTrackView)

    def test_get_object_returns_track_if_current_user(self):
        # Given a mock parent that returns a mock track for current user
        mock_track = Mock()
        mock_track.activity_id.user = self.user
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_track)

        # When getting the object
        track = self.view.get_object(queryset=mock_queryset)

        # Then the mock track will be returned
        assert track == mock_track

    def test_get_object_raised_permission_denied_if_not_owner(self):
        # Given a mock parent that returns a mock track for another user
        mock_track = Mock()
        mock_track.activity_id.user = UserFactory.stub()
        mock_queryset = self.get_mock_queryset_that_returns_mock_object(
            mock_track)

        # When getting the object, Then permission denied will be raised
        with pytest.raises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

    def test_get_context_data_returns_correct_context_data(self):
        # Given a mock track with activity with track count of 1
        self.view.object.activity_id.track.count.return_value = 1

        # When getting the context data
        context = self.view.get_context_data()

        # Then the context indicates that this is the last track
        assert context['last_track'] is True
        assert context['val_errors'] is not None
        assert context['units'] is not None

    def test_get_context_data_returns_correct_context_data_not_last(self):
        # Given a mock track with activity with track count above 1
        self.view.object.activity_id.track.count.return_value = 2

        # When getting the context data
        context = self.view.get_context_data()

        # Then the context indicates that this is not the last track
        assert context['last_track'] is False

    def test_get_context_data_returns_extra_context_data(self):
        # When getting the context data
        context = self.view.get_context_data()

        # Then the val_errors and units fields are included
        assert context['val_errors'] is not None
        assert context['units'] is not None


class TestActivityTrackDownloadView(unittest.TestCase):

    def setUp(self):
        user = UserFactory.stub()
        self.user = user

        class MockActivityTrackDownloadView(ActivityTrackDownloadView):
            """ Mock view with get_object that returns mock"""
            def get_object(self, queryset=None):
                track = Mock()
                track.activity_id.user = user
                track.original_file.file.name = 'Something/file.gpx'
                return track

        self.object = Mock()
        self.request = Mock(spec=HttpRequest)  # type: HttpRequest
        self.request.user = self.user
        self.view = MockActivityTrackDownloadView()

    def test_get_raises_permission_denied_on_bad_user(self):
        # Given a request with another user
        self.request.user = UserFactory.stub()

        # When getting the view, Then a permission denied will be raised
        with pytest.raises(PermissionDenied):
            self.view.get(self.request)

    def test_get_returns_response_with_file(self):
        # When getting the view as the current user
        response = self.view.get(self.request)

        # Then the response will contain the file name in the header
        assert 'file.gpx' in response['Content-Disposition']
        assert 'Something/' not in response['Content-Disposition']
