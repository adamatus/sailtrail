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

    def test_delete_removes_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            file_contents = 'This is testfile'
            test_file = SimpleUploadedFile('test1.txt', 
                                           bytes(file_contents, 'ascii'))

            Activity.objects.create(upfile=test_file)
            a = Activity.objects.first()
            file_path = os.path.join(self.temp_dir, a.upfile.url)
            self.assertTrue(os.path.exists(file_path))

            a.delete()
            self.assertFalse(os.path.exists(file_path))

    def test_delete_removes_only_correct_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            file_contents = 'This is testfile'
            test_file1 = SimpleUploadedFile('test1.txt', 
                                            bytes(file_contents, 'ascii'))
            test_file2 = SimpleUploadedFile('test2.txt', 
                                            bytes(file_contents, 'ascii'))

            Activity.objects.create(upfile=test_file1)
            Activity.objects.create(upfile=test_file2)
            a = Activity.objects.all()[0]
            b = Activity.objects.all()[1]

            a.delete()
            file_path = os.path.join(self.temp_dir, b.upfile.url)
            self.assertTrue(os.path.exists(file_path))

