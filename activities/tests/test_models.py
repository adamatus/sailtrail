from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

import shutil
import tempfile
import os.path

from activities.models import Activity, ActivityDetail


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


class ActivityDetailsModelTests(TestCase):

    fixtures = ['partial-activity.json']

    def test_smoke_model_has_expected_fields(self):
        name = 'Test name'
        desc = 'Test description'

        ActivityDetail.objects.create(
            name=name,
            description=desc,
            file_id=Activity.objects.first())  # Should not raise

    def test_cannot_associate_two_details_with_one_file(self):
        ActivityDetail.objects.create(
            name='Test', file_id=Activity.objects.first())
        self.assertRaises(
            IntegrityError,
            lambda:
                ActivityDetail.objects.create(
                    name='Test2', file_id=Activity.objects.first())
        )

    def test_cannot_create_details_without_file_ref(self):
        self.assertRaises(
            IntegrityError,
            lambda:
                ActivityDetail.objects.create(
                    name='Test')
        )

    def test_cannot_create_details_without_name(self):
        with self.assertRaises(ValidationError):
            a = ActivityDetail.objects.create(
                file_id=Activity.objects.first())
            a.full_clean()

    def test_deleting_activity_removes_activity_details(self):
        ActivityDetail.objects.create(
            name='',
            file_id=Activity.objects.first())  

        self.assertEqual(1, len(ActivityDetail.objects.all()))
        Activity.objects.first().delete()
        self.assertEqual(0, len(ActivityDetail.objects.all()))


