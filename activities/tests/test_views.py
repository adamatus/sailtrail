# import unittest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

import shutil
import tempfile

from activities.models import Activity
from activities.forms import ERROR_NO_UPLOAD_FILE_SELECTED


class HomePageTest(TestCase):
    """Tests for Homepage"""
    fixtures = ['activity.json']

    def test_home_page_renders_home_template(self):
        """Make sure that the homepage is using the correct template"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_shows_existing_filenames(self):
        
        response = self.client.get('/')
        self.assertContains(response, 'kite-session1.sbn')
        self.assertContains(response, 'kite-session2.sbn')


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

    def test_POST_request_redirects_to_homepage(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            """Make sure that we are redirected after POST"""
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes('Testfile', 'ascii'))

            response = self.client.post(reverse('upload'),
                                        data={'upfile': test_file})
            self.assertRedirects(response, '/')

    def test_GET_request_renders_homepage(self):
        response = self.client.get(reverse('upload'))
        self.assertTemplateUsed(response, 'home.html')

    def test_POST_without_file_displays_error(self):
        response = self.client.post(reverse('upload'))
        self.assertContains(response, ERROR_NO_UPLOAD_FILE_SELECTED)


class ActivityViewTest(TestCase):

    fixtures = ['activity.json']

    def test_uses_activity_template(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertTemplateUsed(response, 'activity.html')

    def test_displays_only_details_for_that_session(self):
        response = self.client.get(reverse('view_activity', args=[1]))
        self.assertContains(response, 'kite-session1.sbn')
        self.assertNotContains(response, 'kite-session2.sbn')


class DeleteActivityTest(TestCase):

    fixtures = ['activity.json']

    def test_delete_redirects_to_homepage(self):
        response = self.client.get(reverse('delete_activity', 
                                           args=[1]))
        self.assertRedirects(response, '/')

    def test_delete_removes_item_from_db(self):
        self.client.get(reverse('delete_activity', args=[1]))
        self.assertRaises(ObjectDoesNotExist, 
                          lambda: Activity.objects.get(id=1)
                          )


