# import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

import shutil
import tempfile
import os.path

from activities.models import ActivityTrack, ActivityDetail, ActivityStat
from activities.forms import (UploadFileForm, ActivityDetailsForm,
                              ERROR_NO_UPLOAD_FILE_SELECTED,
                              ERROR_ACTIVITY_NAME_MISSING)


ASSET_PATH = os.path.join(os.path.dirname(__file__),
                          'assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


class HomepageViewTest(TestCase):
    fixtures = ['full-activities.json']

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_home_page_renders_home_template(self):
        """[get] should render the correct template"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_homepage_uses_upload_form(self):
        """[get] should include the upload file form"""
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'],
                              UploadFileForm)

    def test_home_page_shows_existing_activities(self):
        """[get] should show the existing activities"""
        response = self.client.get('/')
        self.assertContains(response, 'First snowkite of the season')
        self.assertContains(response, 'Snowkite lesson:')

    def test_home_page_does_not_show_activities_without_details(self):
        """[get] should not show activities that are missing details"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            ActivityTrack.objects.create(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN)
            )

            response = self.client.get('/')
            self.assertNotContains(response, '></a>')


class FileuploadViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_saving_POST_request(self):
        """[post] should save with valid file"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

            self.client.post(reverse('upload'),
                             data={'upfile': test_file})

            self.assertEqual(ActivityTrack.objects.count(), 1)
            new_activity = ActivityTrack.objects.first()
            self.assertEqual(new_activity.upfile.url,
                             'activities/test1.sbn')

    # TODO This test is very slow as it's actually parsing
    # the uploaded SBN!
    def test_POST_request_redirects_to_new_activity_page(self):
        """[post] should redirect to new activity page"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

            response = self.client.post(reverse('upload'),
                                        data={'upfile': test_file})
            self.assertRedirects(response,
                                 reverse('details',
                                         args=[1]))

    def test_GET_request_renders_homepage(self):
        """[get] should render homepage"""
        response = self.client.get(reverse('upload'))
        self.assertTemplateUsed(response, 'home.html')

    def test_POST_without_file_displays_error(self):
        """[post] should show error when no file was selected"""
        response = self.client.post(reverse('upload'))
        self.assertContains(response, ERROR_NO_UPLOAD_FILE_SELECTED)

    def test_POST_computes_statistics_for_file(self):
        """[post] should compute statistics"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test-stats.sbn', SBN_BIN)

            self.assertEquals(0, ActivityStat.objects.count())
            self.client.post(reverse('upload'),
                             data={'upfile': test_file})
            self.assertEquals(1, ActivityStat.objects.count())


# TODO Many of these tests are SLOOOOWWWW
class NewactivitydetailViewTest(TestCase):

    fixtures = ['full-activities.json']

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_new_view_uses_activity_details_template(self):
        """[get] should render the correct template"""
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_new_view_uses_new_session_form(self):
        """[get] should include the activity details form"""
        response = self.client.get(reverse('details', args=[1]))
        self.assertIsInstance(response.context['form'],
                              ActivityDetailsForm)

    def test_POST_to_new_view_redirects_to_activity(self):
        """[post] should redirect to activity page"""
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        """[post] should save details"""
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        new_details = ActivityDetail.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        """[post] should display error when missing name"""
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)


class ActivitydetailViewTest(TestCase):

    fixtures = ['full-activities.json']

    def test_detail_view_uses_activity_details_template(self):
        """[get] should render the correct template"""
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_detail_view_uses_new_session_form(self):
        """[get] should include the activity details form"""
        response = self.client.get(reverse('details', args=[1]))
        self.assertIsInstance(response.context['form'],
                              ActivityDetailsForm)

    def test_detail_view_shows_current_values(self):
        """[get] should include the activity name/description"""
        details = ActivityTrack.objects.first().details
        response = self.client.get(reverse('details', args=[1]))
        self.assertContains(response, details.name)
        self.assertContains(response, details.description)

    def test_POST_to_detail_view_redirects_to_activity(self):
        """[post] should redirect to activity"""
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        """[post] should save with valid input"""
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        new_details = ActivityDetail.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        """[post] should show error when missing name"""
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)


# TODO This series also very SLOW
class ActivityViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    fixtures = ['full-activities.json']

    def test_uses_activity_template(self):
        """[get] should render the correct template"""
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertTemplateUsed(response, 'activity.html')

    def test_displays_only_details_for_that_session(self):
        """[get] should display details for only that session"""
        response = self.client.get(reverse('view_activity', args=[1]))

        # Expected responses from fixture
        self.assertContains(response, 'First snowkite of the season')
        self.assertContains(response, 'Hooray ice!')
        self.assertNotContains(response, 'Snowkite lesson:')

    def test_html_includes_embedded_track_json(self):
        """[get] should include embedded track JSON"""
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertContains(response, 'var pos = [')

    def test_html_includes_max_speed(self):
        """[get] should include max speed"""
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertContains(response, 'Max speed')
        self.assertContains(response, 'knots')


class DeleteactivityViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.temp_dir):
            ActivityTrack.objects.create(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN)
            )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_delete_redirects_to_homepage(self):
        """[get] should redirect to homepage"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            response = self.client.get(reverse('delete_activity',
                                               args=[1]))
            self.assertRedirects(response, '/')

    def test_delete_removes_item_from_db(self):
        """[get] should remove activity from database"""
        # TODO This test doesn't really match it's description
        with self.settings(MEDIA_ROOT=self.temp_dir):
            self.client.get(reverse('delete_activity', args=[1]))
            self.assertRaises(ObjectDoesNotExist,
                              lambda: ActivityTrack.objects.get(id=1)
                              )
