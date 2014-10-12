from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

import shutil
import tempfile
import os.path

from datetime import datetime, timedelta, time, date
from pytz import timezone

from activities.models import Activity, ActivityDetail, ActivityStat


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


class ActivityStatModelTests(TestCase):

    fixtures = ['partial-activity.json']

    def setUp(self):
        self.stat = ActivityStat(
            datetime=datetime(2014, 10, 12, 11, 20, 15, 
                              tzinfo=timezone('UTC')),
            duration=timedelta(days=0, hours=1, minutes=10),
            file_id=Activity.objects.first())  # Should not raise
        self.stat.save()

    def test_get_start_time_returns_time(self):
        self.assertEqual(time(11, 20, 15), self.stat.start_time)

    def test_get_end_time_returns_correct_time(self):
        self.assertEqual(time(12, 30, 15), self.stat.end_time)

    def test_get_end_date_returns_date(self):
        self.assertEqual(date(2014, 10, 12), self.stat.date)

    def test_get_model_max_speed_is_initially_null(self):
        self.assertEqual(None, self.stat.model_max_speed)

    # TODO This test is very slow, definitely need to mock somehow 
    def test_get_model_max_speed_is_populated_on_call_to_max_speed(self):
        self.assertEqual('21.17 knots', self.stat.max_speed)
        self.assertEqual(10.89, self.stat.model_max_speed)

    def test_get_model_max_speed_is_not_pupulated_if_already_filled(self):
        self.stat.model_max_speed = 10.5
        self.stat.save()
        self.assertEqual('20.41 knots', self.stat.max_speed)


class ActivityModelsIntegrationTests(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_deleting_activity_removes_activity_details(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            Activity.objects.create(
                upfile=SimpleUploadedFile('test.txt', 
                                          bytes('file contents', 'ascii')))

            ActivityDetail.objects.create(
                name='',
                file_id=Activity.objects.first())  

            self.assertEqual(1, len(ActivityDetail.objects.all()))
            Activity.objects.first().delete()
            self.assertEqual(0, len(ActivityDetail.objects.all()))

    def test_model_ordering_on_stat_dates_with_most_recent_first(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            file_contents = 'test file'
            files = ['test{}.txt'.format(x) for x in [1, 2, 3]]
            hours = [11, 10, 12]
            test_files = []
            for f, t in zip(files, hours):
                test_files.append(SimpleUploadedFile(f, 
                                                     bytes(file_contents, 
                                                           'ascii')))
                a = Activity.objects.create(upfile=test_files[-1])

                ActivityStat.objects.create(
                    datetime=datetime(2014, 10, 12, t, 20, 15, 
                                      tzinfo=timezone('UTC')),
                    duration=timedelta(days=0, hours=1, minutes=10),
                    file_id=a)

            activities = Activity.objects.all()
            self.assertIn('test3.txt', activities[0].upfile.url)
            self.assertIn('test1.txt', activities[1].upfile.url)
            self.assertIn('test2.txt', activities[2].upfile.url)
