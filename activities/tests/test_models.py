from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

import shutil
import tempfile
import os.path

from activities.models import Activity


class ActivityModelTest(TestCase):
    """Tests for the Activity model"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_upfile_field_creates_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes('This is testfile', 'ascii'))
            Activity.objects.create(upfile=test_file)
            a = Activity.objects.first()

            self.assertTrue(
                os.path.exists(
                    os.path.join(self.temp_dir, a.upfile.url)
                ))

    def test_upfile_file_contents_are_correct(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            file_contents = 'This is testfile'
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes(file_contents, 'ascii'))
                                           
            Activity.objects.create(upfile=test_file)
            a = Activity.objects.first()

            with open(os.path.join(self.temp_dir, a.upfile.url), 'r') as f:
                self.assertEqual(
                    f.read(),
                    file_contents
                )

