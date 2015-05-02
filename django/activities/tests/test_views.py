# import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

User = get_user_model()

import shutil
import tempfile
import os.path

from activities.models import (Activity, ActivityTrack,
                               ActivityDetail, ActivityStat)
from activities.forms import (UploadFileForm, ActivityDetailsForm,
                              ERROR_NO_UPLOAD_FILE_SELECTED,
                              ERROR_ACTIVITY_NAME_MISSING,
                              ERROR_ACTIVITY_CATEGORY_MISSING)

from .factories import UserFactory, ActivityFactory, ActivityDetailFactory


ASSET_PATH = os.path.join(os.path.dirname(__file__),
                          'assets')

with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


class HomepageViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        ActivityDetailFactory.create(
            name="First snowkite of the season")
        ActivityDetailFactory.create(
            name="Snowkite lesson:")

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
            a = Activity.objects.create(user=UserFactory.create())
            ActivityTrack.create_new(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN),
                activity_id=a
            )

            response = self.client.get('/')
            self.assertNotContains(response, '></a>')


class FileuploadViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')

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
            self.assertEqual(new_activity.original_filename,
                             'test1.sbn')

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


class NewactivitydetailViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        user = UserFactory.create(username="test")
        activity = ActivityFactory(user=user)
        ActivityDetailFactory.create(activity_id=activity)
        self.client.login(username='test', password='password')

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
                  'category': 'SK',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        """[post] should save details"""
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'category': 'SK',
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
                  'category': 'SK',
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)

    def test_POST_without_category_displays_error(self):
        """[post] should display error when missing category"""
        name = 'Name'
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_CATEGORY_MISSING)


class ActivitydetailViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        user = UserFactory.create(username="test")
        activity = ActivityFactory(user=user)
        ActivityDetailFactory.create(activity_id=activity)
        self.client.login(username='test', password='password')

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
        details = Activity.objects.first().details
        response = self.client.get(reverse('details', args=[1]))
        self.assertContains(response, details.name)
        self.assertContains(response, details.description)

    def test_POST_to_detail_view_redirects_to_activity(self):
        """[post] should redirect to activity"""
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'category': 'SK',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        """[post] should save with valid input"""
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'category': 'SK',
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
        ActivityDetailFactory.create(
            name="First snowkite of the season",
            description="Hooray ice!")
        ActivityDetailFactory.create(
            name="Snowkite Lesson: C-lesson",
            description="Less riding during lessons")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

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

    def test_html_includes_max_speed(self):
        """[get] should include max speed"""
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertContains(response, 'Max speed')
        self.assertContains(response, 'knots')


class DeleteactivityViewTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')
        with self.settings(MEDIA_ROOT=self.temp_dir):
            Activity.objects.create(user=self.user)

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
        with self.settings(MEDIA_ROOT=self.temp_dir):
            self.client.get(reverse('delete_activity', args=[1]))
            self.assertRaises(ObjectDoesNotExist,
                              lambda: Activity.objects.get(id=1)
                              )
