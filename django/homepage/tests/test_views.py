import os.path
import tempfile
from unittest.mock import patch, sentinel, MagicMock

import pytest
import unittest

import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from homepage.views import HomePageView
from api.models import Activity, ActivityTrack
from api.tests.factories import (ActivityFactory, ActivityTrackFactory,
                                 ActivityTrackpointFactory)
from core.forms import UploadFileForm
from users.tests.factories import UserFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__),
                          '../../activities/tests/assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


class TestHomepageView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        view = HomePageView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('homepage.views.Helper')
    def test_get_queryset_calls_through_to_helper(self, mock_helper):

        mock_helper.get_activities = MagicMock()
        mock_helper.get_activities.return_value = sentinel.activity_list

        queryset = self.view.get_queryset()

        mock_helper.get_activities.assert_called_once_with(self.user)

        self.assertEqual(queryset, sentinel.activity_list)

    @patch('homepage.views.Helper')
    def test_get_context_data_populates_leaders(self, mock_helper):

        mock_helper.get_leaders = MagicMock()
        mock_helper.get_leaders.return_value = sentinel.leaders

        context = self.view.get_context_data()

        mock_helper.get_leaders.assert_called_once_with()

        self.assertEqual(context['leaders'], sentinel.leaders)


@pytest.mark.integration
class TestHomepageViewIntegration(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_home_page_renders_home_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_homepage_uses_upload_form(self):
        response = self.client.get(reverse('home'))
        self.assertIsInstance(response.context['upload_form'],
                              UploadFileForm)

    def test_home_page_shows_existing_activities(self):
        a = ActivityFactory.create(
            name="First snowkite of the season")
        t = ActivityTrackFactory.create(activity_id=a)
        ActivityTrackpointFactory.create(track_id=t)
        t.initialize_stats()
        a = ActivityFactory.create(
            name="Snowkite lesson:")
        t = ActivityTrackFactory.create(activity_id=a)
        ActivityTrackpointFactory.create(track_id=t)
        t.initialize_stats()

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'First snowkite of the season')
        self.assertContains(response, 'Snowkite lesson:')

    def test_home_page_does_not_show_activities_without_details(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            a = Activity.objects.create(user=UserFactory.create())
            ActivityTrack.create_new(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN),
                activity_id=a
            )

            response = self.client.get(reverse('home'))
            self.assertNotContains(response, '></a>')
