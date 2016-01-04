from unittest.mock import patch, sentinel, MagicMock, Mock

import unittest

import pytest
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from activities.views import UploadView, UploadTrackView, \
    DetailsView, ActivityTrackView, ActivityView, ActivityTrackDownloadView
from users.tests.factories import UserFactory


class ViewMockMixin:

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user


class TestUploadView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestUploadView, self).setUp()
        self.request.POST = sentinel.POST
        self.request.FILES = sentinel.FILES
        self.view = UploadView()

    @patch('activities.views.UploadFileForm')
    def test_post_raises_suspicious_operation_on_bad_form(self,
                                                          upload_form_mock):
        form = Mock()
        form.is_valid.return_value = False
        upload_form_mock.return_value = form

        with self.assertRaises(SuspiciousOperation):
            self.view.post(self.request)

        upload_form_mock.assert_called_with(sentinel.POST, sentinel.FILES)

    @patch('activities.views.redirect')
    @patch('activities.views.create_new_activity_for_user')
    @patch('activities.views.UploadFileForm')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            upload_form_mock,
                                                            helper_mock,
                                                            redirect_mock):
        form = Mock()
        form.is_valid.return_value = True
        form.cleaned_data = dict(upfile=[sentinel.file1, sentinel.file2])
        upload_form_mock.return_value = form

        created_mock = MagicMock()
        created_mock.id = sentinel.id
        helper_mock.return_value = created_mock

        redirect_mock.return_value = sentinel.response

        response = self.view.post(self.request)

        helper_mock.assert_called_with(user=self.request.user)
        created_mock.add_track.assert_any_call(sentinel.file1)
        created_mock.add_track.assert_any_call(sentinel.file2)

        redirect_mock.assert_called_with('details', sentinel.id)

        self.assertEqual(response, sentinel.response)


class TestUploadTrackView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestUploadTrackView, self).setUp()
        self.request.POST = sentinel.POST
        self.request.FILES = sentinel.FILES
        self.view = UploadTrackView()

    @patch('activities.views.get_activity_by_id')
    def test_post_raises_permission_denied_if_not_owner(self,
                                                        helper_mock):
        found_activity = MagicMock()
        found_activity.user = UserFactory.stub()
        helper_mock.return_value = found_activity

        with self.assertRaises(PermissionDenied):
            self.view.post(self.request, sentinel.activity_id)

        helper_mock.assert_called_with(sentinel.activity_id)

    @patch('activities.views.UploadFileForm')
    @patch('activities.views.get_activity_by_id')
    def test_post_raises_suspicious_operation_on_bad_form(self,
                                                          helper_mock,
                                                          upload_form_mock):
        found_activity = MagicMock()
        found_activity.user = self.user
        helper_mock.return_value = found_activity

        form = Mock()
        form.is_valid.return_value = False
        upload_form_mock.return_value = form

        with self.assertRaises(SuspiciousOperation):
            self.view.post(self.request, sentinel.activity_id)

        upload_form_mock.assert_called_with(sentinel.POST, sentinel.FILES)

    @patch('activities.views.redirect')
    @patch('activities.views.get_activity_by_id')
    @patch('activities.views.UploadFileForm')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            upload_form_mock,
                                                            helper_mock,
                                                            redirect_mock):
        found_activity = MagicMock()
        found_activity.user = self.user
        found_activity.id = sentinel.id
        helper_mock.return_value = found_activity

        form = Mock()
        form.is_valid.return_value = True
        form.cleaned_data = dict(upfile=[sentinel.file1, sentinel.file2])
        upload_form_mock.return_value = form

        redirect_mock.return_value = sentinel.response

        response = self.view.post(self.request, sentinel.activity_id)

        found_activity.add_track.assert_any_call(sentinel.file1)
        found_activity.add_track.assert_any_call(sentinel.file2)

        redirect_mock.assert_called_with('view_activity', pk=sentinel.id)

        self.assertEqual(response, sentinel.response)


class TestDetailsView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestDetailsView, self).setUp()
        view = DetailsView()
        view.request = self.request
        view.object = Mock()
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        self.view = view

    def get_mock_queryset_and_activity(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_activity = Mock()
        mock_activity.user = self.user
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_activity

        return mock_queryset, mock_activity

    def test_get_object_returns_activity_if_current_user(self):
        mock_queryset, mock_activity = self.get_mock_queryset_and_activity()

        activity = self.view.get_object(queryset=mock_queryset)

        self.assertEqual(activity, mock_activity)

    def test_get_object_raises_permission_error_if_not_current_user(self):
        mock_queryset, mock_activity = self.get_mock_queryset_and_activity()
        mock_activity.user = UserFactory.stub()

        with self.assertRaises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

    def test_get_context_adds_delete_cancel_link(self):
        self.view.object.id = 1
        self.view.object.name = None

        context = self.view.get_context_data()

        link = reverse('delete_activity', args=[1])

        self.assertEqual(context['cancel_link'], link)

    def test_get_context_adds_view_cancel_link(self):
        self.view.object.id = 1
        self.view.object.name = 'Something'

        context = self.view.get_context_data()

        link = reverse('view_activity', args=[1])

        self.assertEqual(context['cancel_link'], link)


class TestActivityView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestActivityView, self).setUp()
        view = ActivityView()
        view.request = self.request
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        view.object = Mock()
        self.view = view

    def get_mock_queryset_and_activity(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_activity = Mock()
        mock_activity.user = self.user
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_activity

        return mock_queryset, mock_activity

    @patch('activities.views.verify_private_owner')
    def test_get_object_returns_activity(self, helper: MagicMock):
        mock_queryset, mock_activity = self.get_mock_queryset_and_activity()

        activity = self.view.get_object(queryset=mock_queryset)

        assert activity == mock_activity
        helper.assert_called_with(mock_activity, self.request)

    @patch('activities.views.verify_private_owner')
    def test_get_object_raises_permission_denied(self, helper: MagicMock):
        mock_queryset, mock_activity = self.get_mock_queryset_and_activity()

        helper.side_effect = PermissionDenied

        with pytest.raises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

    def test_get_context_adds_units_and_errors(self):
        context = self.view.get_context_data()
        assert context['val_errors'] is not None
        assert context['units'] is not None


class TestActivityTrackView(ViewMockMixin, unittest.TestCase):

    def setUp(self):
        super(TestActivityTrackView, self).setUp()
        view = ActivityTrackView()
        view.request = self.request
        view.object = Mock()
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        self.view = view

    def get_create_mock_queryset(self):
        """Setup chained mocks to return a mock_track"""
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_track = Mock()

        mock_track.activity_id.user = self.user
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_track

        return mock_queryset, mock_track

    def test_get_object_returns_track_if_current_user(self):
        mock_queryset, mock_track = self.get_create_mock_queryset()

        track = self.view.get_object(queryset=mock_queryset)

        self.assertEqual(track, mock_track)

    def test_get_object_raised_permission_denied_if_not_owner(self):
        mock_queryset, mock_track = self.get_create_mock_queryset()
        mock_track.activity_id.user = UserFactory.stub()

        with self.assertRaises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)

    def test_get_context_data_returns_correct_context_data(self):
        self.view.object.activity_id.track.count.return_value = 1

        context = self.view.get_context_data()
        assert context['val_errors'] is not None
        assert context['units'] is not None
        assert context['last_track'] is True

    def test_get_context_data_returns_correct_context_data_not_last(self):
        self.view.object.activity_id.track.count.return_value = 2

        context = self.view.get_context_data()
        assert context['last_track'] is False


class TestActivityTrackDownloadView(unittest.TestCase):

    def setUp(self):

        user = UserFactory.stub()
        self.user = user

        class MockActivityTrackDownloadView(ActivityTrackDownloadView):
            """ Mock view with get_object that returns mock"""
            def get_object(self):
                track = Mock()
                track.activity_id.user = user
                track.original_file.file.name = 'Something/file.gpx'
                return track

        self.object = Mock()
        self.request = RequestFactory
        self.request.user = self.user
        self.view = MockActivityTrackDownloadView()

    def test_get_raises_permission_denied_on_bad_user(self):
        self.request.user = UserFactory.stub()
        with pytest.raises(PermissionDenied):
            self.view.get(self.request)

    def test_get_returns_response_with_file(self):
        response = self.view.get(self.request)

        assert 'file.gpx' in response['Content-Disposition']
        assert 'Something/' not in response['Content-Disposition']
