import os.path
import shutil
import tempfile

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
from users.tests.factories import UserFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


@pytest.mark.django_db
@pytest.mark.integration
class TestActivityDetailsFormIntegration:

    def test_form_renders_correct_fields(self):
        form = ActivityDetailsForm()
        assert 'id_name' in form.as_p()

    def test_form_save(self):
        a = ActivityFactory.create()
        form = ActivityDetailsForm({'name': 'Test',
                                    'description': '',
                                    'category': 'IB'},
                                   instance=a)
        form.is_valid()
        upactivity = form.save()
        assert upactivity is not None
        assert upactivity.name == 'Test'


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

            assert ActivityTrack.objects.count() == 1
            new_activity = ActivityTrack.objects.first()
            assert new_activity.original_filename == 'test1.sbn'

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


@pytest.mark.integration
class TestNewActivityDetailViewIntegration(TestCase):

    def setUp(self):
        user = UserFactory.create(username="test")
        a = ActivityFactory(user=user)
        t = ActivityTrackFactory.create(activity=a)
        ActivityTrackpointFactory.create(track=t)
        t.reset_trim()
        self.client.login(username='test', password='password')

    def test_new_view_uses_activity_details_template(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_new_view_uses_new_session_form(self):
        response = self.client.get(reverse('details', args=[1]))
        assert isinstance(response.context['form'], ActivityDetailsForm)

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
        assert new_details.name == name

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
        t = ActivityTrackFactory.create(activity=a)
        ActivityTrackpointFactory.create(track=t)
        t.reset_trim()
        self.client.login(username='test', password='password')

    def test_detail_view_uses_activity_details_template(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_detail_view_uses_new_session_form(self):
        response = self.client.get(reverse('details', args=[1]))
        assert isinstance(response.context['form'], ActivityDetailsForm)

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
        assert new_details.name == name

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
        t = ActivityTrackFactory.create(activity=a)
        ActivityTrackpointFactory.create(track=t)
        t.reset_trim()

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
