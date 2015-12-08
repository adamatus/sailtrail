import os.path
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from activities.forms import (ActivityDetailsForm,
                              ERROR_ACTIVITY_NAME_MISSING,
                              ERROR_ACTIVITY_CATEGORY_MISSING)
from api.models import Activity, ActivityTrack
from api.tests.factories import (ActivityFactory, ActivityTrackFactory,
                                 ActivityTrackpointFactory)
from core.forms import UploadFileForm
from users.tests.factories import UserFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


@pytest.mark.integration
class TestHomepageViewIntegration(TestCase):

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
        a = Activity.objects.create(user=UserFactory.create())
        ActivityTrack.create_new(
            upfile=SimpleUploadedFile('test1.sbn', SBN_BIN),
            activity_id=a
        )

        response = self.client.get(reverse('home'))
        self.assertNotContains(response, '></a>')


@pytest.mark.integration
class TestFileUploadView(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')

    def test_saving_POST_request(self):
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
        test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

        response = self.client.post(reverse('upload'),
                                    data={'upfile': test_file})
        self.assertRedirects(response,
                             reverse('details',
                                     args=[1]))


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
