# import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

import shutil
import tempfile

from activities.models import Activity, ActivityDetail
from activities.forms import (ActivityDetailsForm, 
                              ERROR_NO_UPLOAD_FILE_SELECTED,
                              ERROR_ACTIVITY_NAME_MISSING)


class HomePageTest(TestCase):
    """Tests for Homepage"""
    fixtures = ['full-activities.json']

    def test_home_page_renders_home_template(self):
        """Make sure that the homepage is using the correct template"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_shows_existing_activities(self):
        
        response = self.client.get('/')
        self.assertContains(response, 'First kite session')
        self.assertContains(response, 'Kiting times 2')

    def test_home_page_does_not_show_activities_without_details(self):
        Activity.objects.create(
            upfile=SimpleUploadedFile('test1.txt', 
                                      bytes('Testfile', 'ascii'))
        )
        
        response = self.client.get('/')
        self.assertNotContains(response, '></a>')


class FileUploadTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_saving_POST_request(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            """Make sure that the upload filename is saved"""
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes('Testfile', 'ascii'))

            self.client.post(reverse('upload'),
                             data={'upfile': test_file})

            self.assertEqual(Activity.objects.count(), 1)
            new_activity = Activity.objects.first()
            self.assertEqual(new_activity.upfile.url,
                             'activities/test1.txt')

    def test_POST_request_redirects_to_new_activity_page(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            """Make sure that we are redirected after POST"""
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes('Testfile', 'ascii'))

            response = self.client.post(reverse('upload'),
                                        data={'upfile': test_file})
            self.assertRedirects(response, 
                                 reverse('details', 
                                         args=[1]))

    def test_GET_request_renders_homepage(self):
        response = self.client.get(reverse('upload'))
        self.assertTemplateUsed(response, 'home.html')

    def test_POST_without_file_displays_error(self):
        response = self.client.post(reverse('upload'))
        self.assertContains(response, ERROR_NO_UPLOAD_FILE_SELECTED)


class NewActivityDetailViewTest(TestCase):

    fixtures = ['partial-activity.json']

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
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        new_details = ActivityDetail.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)


class ActivityDetailViewTest(TestCase):

    fixtures = ['full-activities.json']

    def test_detail_view_uses_activity_details_template(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertTemplateUsed(response, 'activity_details.html')

    def test_detail_view_uses_new_session_form(self):
        response = self.client.get(reverse('details', args=[1]))
        self.assertIsInstance(response.context['form'], 
                              ActivityDetailsForm)

    def test_detail_view_shows_current_values(self):
        details = Activity.objects.first().details
        response = self.client.get(reverse('details', args=[1]))
        self.assertContains(response, details.name)
        self.assertContains(response, details.description)

    def test_POST_to_detail_view_redirects_to_activity(self):
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': 'Test post',
                  'description': 'Test description'})
        self.assertRedirects(response, reverse('view_activity', args=[1]))

    def test_POST_with_valid_input_saves_details(self):
        name = 'Test name'
        desc = 'Test description'
        self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        new_details = ActivityDetail.objects.first()
        self.assertEqual(new_details.name, name)

    def test_POST_without_name_displays_error(self):
        name = ''
        desc = 'Test description'
        response = self.client.post(
            reverse('details', args=[1]),
            data={'name': name,
                  'description': desc})
        self.assertContains(response, ERROR_ACTIVITY_NAME_MISSING)


class ActivityViewTest(TestCase):

    fixtures = ['full-activities.json']

    def test_uses_activity_template(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertTemplateUsed(response, 'activity.html')

    def test_displays_only_details_for_that_session(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        
        # Expected responses from fixture
        self.assertContains(response, 'First kite session')
        self.assertContains(response, 'Bet it was awesome')
        self.assertNotContains(response, 'Kiting times 2')


class DeleteActivityTest(TestCase):

    fixtures = ['full-activities.json']

    def test_delete_redirects_to_homepage(self):
        response = self.client.get(reverse('delete_activity', 
                                           args=[1]))
        self.assertRedirects(response, '/')

    def test_delete_removes_item_from_db(self):
        self.client.get(reverse('delete_activity', args=[1]))
        self.assertRaises(ObjectDoesNotExist, 
                          lambda: Activity.objects.get(id=1)
                          )


