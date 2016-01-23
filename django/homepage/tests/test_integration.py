import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from api.models import Activity, ActivityTrack
from api.tests.factories import (ActivityFactory, ActivityTrackFactory,
                                 ActivityTrackpointFactory)
from core.forms import UploadFileForm
from tests.assets import get_test_file_data
from tests.utils import FileDeleter
from users.tests.factories import UserFactory

SBN_BIN = get_test_file_data('tiny.SBN')


@pytest.mark.integration
class TestHomepageViewIntegration(FileDeleter, TestCase):

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
        t = ActivityTrackFactory.create(activity=a)
        ActivityTrackpointFactory.create(track=t)
        t.reset_trim()
        a = ActivityFactory.create(
            name="Snowkite lesson:")
        t = ActivityTrackFactory.create(activity=a)
        ActivityTrackpointFactory.create(track=t)
        t.reset_trim()

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'First snowkite of the season')
        self.assertContains(response, 'Snowkite lesson:')

    def test_home_page_does_not_show_activities_without_details(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            a = Activity.objects.create(user=UserFactory.create())
            ActivityTrack.create_new(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN),
                activity=a
            )

            response = self.client.get(reverse('home'))
            self.assertNotContains(response, '></a>')
