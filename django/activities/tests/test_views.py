import os.path
import shutil
import tempfile
from unittest.mock import patch, sentinel, MagicMock, Mock

import pytest
import unittest

from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from activities.forms import (ActivityDetailsForm,
                              ERROR_ACTIVITY_NAME_MISSING,
                              ERROR_ACTIVITY_CATEGORY_MISSING)
from activities.views import UploadView, UploadTrackView, \
    DetailsView, ActivityTrackView
from api.models import Activity, ActivityTrack
from api.tests.factories import (ActivityFactory, ActivityTrackFactory,
                                 ActivityTrackpointFactory)
from users.tests.factories import UserFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


class TestFileUploadView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
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
    @patch('activities.views.Activity')
    @patch('activities.views.UploadFileForm')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            upload_form_mock,
                                                            activity_mock,
                                                            redirect_mock):
        form = Mock()
        form.is_valid.return_value = True
        form.cleaned_data = dict(upfile=[sentinel.file1, sentinel.file2])
        upload_form_mock.return_value = form

        created_mock = MagicMock()
        created_mock.id = sentinel.id
        activity_mock.objects.create.return_value = created_mock

        redirect_mock.return_value = sentinel.response

        response = self.view.post(self.request)

        activity_mock.objects.create.assert_called_with(user=self.request.user)
        created_mock.add_track.assert_any_call(sentinel.file1)
        created_mock.add_track.assert_any_call(sentinel.file2)

        redirect_mock.assert_called_with('details', sentinel.id)

        self.assertEqual(response, sentinel.response)


class TestUploadTrackView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        self.request.POST = sentinel.POST
        self.request.FILES = sentinel.FILES
        self.view = UploadTrackView()

    @patch('activities.views.Activity')
    def test_post_raises_permission_denied_if_not_owner(self,
                                                        activity_mock):
        found_activity = MagicMock()
        found_activity.user = UserFactory.stub()
        activity_mock.objects.get.return_value = found_activity

        with self.assertRaises(PermissionDenied):
            self.view.post(self.request, sentinel.activity_id)

        activity_mock.objects.get.assert_called_with(id=sentinel.activity_id)

    @patch('activities.views.UploadFileForm')
    @patch('activities.views.Activity')
    def test_post_raises_suspicious_operation_on_bad_form(self,
                                                          activity_mock,
                                                          upload_form_mock):
        found_activity = MagicMock()
        found_activity.user = self.user
        activity_mock.objects.get.return_value = found_activity

        form = Mock()
        form.is_valid.return_value = False
        upload_form_mock.return_value = form

        with self.assertRaises(SuspiciousOperation):
            self.view.post(self.request, sentinel.activity_id)

        upload_form_mock.assert_called_with(sentinel.POST, sentinel.FILES)

    @patch('activities.views.redirect')
    @patch('activities.views.Activity')
    @patch('activities.views.UploadFileForm')
    def test_post_creates_track_for_each_file_and_redirects(self,
                                                            upload_form_mock,
                                                            activity_mock,
                                                            redirect_mock):
        found_activity = MagicMock()
        found_activity.user = self.user
        found_activity.id = sentinel.id
        activity_mock.objects.get.return_value = found_activity

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


@pytest.mark.integration
class TestFileUploadViewIntegration(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_saving_POST_request(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

            self.client.post(reverse('upload'),
                             data={'upfile': test_file})

            self.assertEqual(ActivityTrack.objects.count(), 1)
            new_activity = ActivityTrack.objects.first()
            self.assertEqual(new_activity.original_filename,
                             'test1.sbn')

    # TODO This test is very slow as it's actually parsing
    # the uploaded SBN!
    def test_POST_request_redirects_to_new_activity_page(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

            response = self.client.post(reverse('upload'),
                                        data={'upfile': test_file})
            self.assertRedirects(response,
                                 reverse('details',
                                         args=[1]))


class TestDetailsView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        view = DetailsView()
        view.request = self.request
        view.object = Mock()
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        self.view = view

    def test_get_object_returns_activity_if_current_user(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_activity = Mock()
        mock_activity.user = self.user
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_activity

        activity = self.view.get_object(queryset=mock_queryset)

        self.assertEqual(activity, mock_activity)

    def test_get_object_raises_persmission_error_if_not_current_user(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_activity = Mock()
        mock_activity.user = UserFactory.stub()
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_activity

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


@pytest.mark.integration
class TestNewActivityDetailViewIntegration(TestCase):

    def setUp(self):
        user = UserFactory.create(username="test")
        a = ActivityFactory(user=user)
        t = ActivityTrackFactory.create(activity_id=a)
        ActivityTrackpointFactory.create(track_id=t)
        t.initialize_stats()
        self.client.login(username='test', password='password')

    def test_new_view_uses_activity_details_template(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_new_view_uses_new_session_form(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertIsInstance(response.context['form'],
                              ActivityDetailsForm)

    def test_POST_to_new_view_redirects_to_activity(self):
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'category': 'SK',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'category': 'SK',
                  'description': desc})
        new_details = Activity.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'category': 'SK',
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)

    def test_POST_without_category_displays_error(self):
        name = 'Name'
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_CATEGORY_MISSING)


@pytest.mark.integration
class TestActivityDetailViewIntegration(TestCase):

    def setUp(self):
        user = UserFactory.create(username="test")
        a = ActivityFactory(user=user)
        t = ActivityTrackFactory.create(activity_id=a)
        ActivityTrackpointFactory.create(track_id=t)
        t.initialize_stats()
        self.client.login(username='test', password='password')

    def test_detail_view_uses_activity_details_template(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_detail_view_uses_new_session_form(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertIsInstance(response.context['form'],
                              ActivityDetailsForm)

    def test_detail_view_shows_current_values(self):
        details = Activity.objects.first()
        response = self.client.get(reverse('details', args=[1]))
        self.assertContains(response, details.name)
        self.assertContains(response, details.description)

    def test_POST_to_detail_view_redirects_to_activity(self):
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'category': 'SK',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'category': 'SK',
                  'description': desc})
        new_details = Activity.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)


@pytest.mark.integration
class TestActivityViewIntegration(TestCase):

    def setUp(self):
        a = ActivityFactory.create(
            name="First snowkite of the season",
            description="Hooray ice!")
        t = ActivityTrackFactory.create(activity_id=a)
        ActivityTrackpointFactory.create(track_id=t)
        t.initialize_stats()

    def test_uses_activity_template(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertTemplateUsed(response, 'activity.html')

    def test_displays_only_details_for_that_session(self):
        response = self.client.get(reverse('view_activity', args=[1]))

        # Expected responses from fixture
        self.assertContains(response, 'First snowkite of the season')
        self.assertContains(response, 'Hooray ice!')
        self.assertNotContains(response, 'Snowkite lesson:')

    def test_html_includes_max_speed(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertContains(response, 'Max Speed')
        self.assertContains(response, 'knots')


class TesActivityTrackView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        view = ActivityTrackView()
        view.request = self.request
        view.object = Mock()
        view.pk_url_kwarg = 'pk'
        view.kwargs = dict(pk=1)
        self.view = view

    def test_get_object_returns_track_if_current_user(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_track = Mock()
        mock_track.activity_id.user = self.user
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_track

        activity = self.view.get_object(queryset=mock_queryset)

        self.assertEqual(activity, mock_track)

    def test_get_object_raised_permission_denied_if_not_owner(self):
        mock_queryset = Mock()
        mock_queryset2 = Mock()
        mock_track = Mock()
        mock_track.activity_id.user = UserFactory.stub()
        mock_queryset.filter.return_value = mock_queryset2
        mock_queryset2.get.return_value = mock_track

        with self.assertRaises(PermissionDenied):
            self.view.get_object(queryset=mock_queryset)
