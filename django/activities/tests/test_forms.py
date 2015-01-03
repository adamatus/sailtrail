from django.test import TestCase

import shutil
import tempfile
import os.path

from django.core.files.uploadedfile import SimpleUploadedFile

from activities.forms import UploadFileForm, ActivityDetailsForm
from activities.models import Activity, ActivityDetail

ASSET_PATH = os.path.join(os.path.dirname(__file__), 
                          'assets')


class UploadFileFormTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_form_renders_file_upload_field(self):
        """Smoke test to make sure we get the input type we want"""
        form = UploadFileForm()
        self.assertIn('id_upfile', form.as_p())

    def test_form_save(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
                sbn_bin = f.read()
            upfile = SimpleUploadedFile('test.txt', sbn_bin)
            form = UploadFileForm({}, {'upfile': upfile})
            form.is_valid()
            upactivity = form.save()
            self.assertNotEquals(upactivity, None)
            self.assertEqual(upactivity,
                             Activity.objects.first())


class ActivityDetailsFormTest(TestCase):

    fixtures = ['partial-activity.json']

    def test_form_renders_correct_fields(self):
        form = ActivityDetailsForm()
        self.assertIn('id_name', form.as_p())

    def test_from_save(self):
        a = Activity.objects.first()
        form = ActivityDetailsForm({'name': 'Test', 
                                    'description': '', 
                                    'file_id': a.id})
        form.is_valid()
        upactivity = form.save()
        self.assertNotEquals(upactivity, None)
        self.assertEqual(upactivity,
                         ActivityDetail.objects.first())
