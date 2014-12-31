from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

import shutil
import tempfile
import os.path

from datetime import datetime, timedelta, time, date
from pytz import timezone

from activities.models import (Activity, ActivityDetail, ActivityStat,
                               ActivityTrackpoint)

ASSET_PATH = os.path.join(os.path.dirname(__file__), 
                          'assets')
with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()


class ActivityModelTest(TestCase):
    """Tests for the Activity model"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_upfile_field_creates_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)
                                           
            Activity.objects.create(upfile=test_file)
            a = Activity.objects.first()

            self.assertTrue(
                os.path.exists(
                    os.path.join(self.temp_dir, a.upfile.url)
                ))

    def test_delete_removes_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)

            Activity.objects.create(upfile=test_file)
            a = Activity.objects.first()
            file_path = os.path.join(self.temp_dir, a.upfile.url)
            self.assertTrue(os.path.exists(file_path))

            a.delete()
            self.assertFalse(os.path.exists(file_path))

    def test_delete_removes_only_correct_file(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            test_file2 = SimpleUploadedFile('test2.sbn', SBN_BIN)

            Activity.objects.create(upfile=test_file1)
            Activity.objects.create(upfile=test_file2)
            a = Activity.objects.all()[0]
            b = Activity.objects.all()[1]

            a.delete()
            file_path = os.path.join(self.temp_dir, b.upfile.url)
            self.assertTrue(os.path.exists(file_path))

    def test_model_ordering_on_dates_with_most_recent_first(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            files = ['test{}.sbn'.format(x) for x in [1, 2, 3]]
            hours = [11, 10, 12]
            test_files = []
            for f, t in zip(files, hours):
                test_files.append(SimpleUploadedFile(f, SBN_BIN))
                a = Activity.objects.create(upfile=test_files[-1])

                a.trim_start=datetime(2014, 10, 12, t, 20, 15, 
                                          tzinfo=timezone('UTC'))
                a.save()

            activities = Activity.objects.all()
            self.assertIn('test3.sbn', activities[0].upfile.url)
            self.assertIn('test1.sbn', activities[1].upfile.url)
            self.assertIn('test2.sbn', activities[2].upfile.url)

    def test_integration_get_trackpoints_returns_points(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = Activity.objects.create(upfile=test_file1)
            tps = a.get_trackpoints()
            self.assertEquals(4, len(tps))
            self.assertAlmostEquals(1, tps[0].id)
            self.assertAlmostEquals(4, tps[3].id)

    def test_integration_get_trackpoints_returns_points_with_start_time(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = Activity.objects.create(upfile=test_file1)
            a.trim_start = datetime(2014, 7, 15, 22, 37, 55, 
                                    tzinfo=timezone('UTC'))
            a.save()
            tps = a.get_trackpoints()
            self.assertEquals(3, len(tps))
            self.assertAlmostEquals(2, tps[0].id)
            self.assertAlmostEquals(4, tps[2].id)

    def test_integration_get_trackpoints_returns_points_with_end_time(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = Activity.objects.create(upfile=test_file1)
            a.trim_end = datetime(2014, 7, 15, 22, 37, 56, 
                                  tzinfo=timezone('UTC'))
            a.save()
            tps = a.get_trackpoints()
            self.assertEquals(3, len(tps))
            self.assertAlmostEquals(1, tps[0].id)
            self.assertAlmostEquals(3, tps[2].id)

    def test_integration_get_trackpoints_returns_points_with_both_time(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = Activity(upfile=test_file1)
            a.save()
            a.trim_start = datetime(2014, 7, 15, 22, 37, 55, 
                                    tzinfo=timezone('UTC'))
            a.trim_end = datetime(2014, 7, 15, 22, 37, 56, 
                                  tzinfo=timezone('UTC'))
            a.save()
            tps = a.get_trackpoints()
            self.assertEquals(2, len(tps))
            self.assertAlmostEquals(2, tps[0].id)
            self.assertAlmostEquals(3, tps[1].id)


class ActivityTrackpointTests(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_integration_upload_creates_trackpoints(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)
            self.assertEquals(0, len(ActivityTrackpoint.objects.all()))
            Activity.objects.create(upfile=test_file)
            self.assertEquals(4, len(ActivityTrackpoint.objects.all()))
            first = ActivityTrackpoint.objects.first()
            last = ActivityTrackpoint.objects.last()
            self.assertAlmostEquals(43.0875531, first.lat)
            self.assertAlmostEquals(-89.3895205, first.lon)
            self.assertAlmostEquals(3.11, first.sog)
            self.assertEquals(7, first.timepoint.month)
            self.assertEquals(15, first.timepoint.day)
            self.assertEquals(22, first.timepoint.hour)
            self.assertEquals(54, first.timepoint.second)
            self.assertAlmostEquals(43.0875511, last.lat)
            self.assertAlmostEquals(-89.3896433, last.lon)
            self.assertAlmostEquals(3.42, last.sog)
            self.assertEquals(7, last.timepoint.month)
            self.assertEquals(15, last.timepoint.day)
            self.assertEquals(22, last.timepoint.hour)
            self.assertEquals(57, last.timepoint.second)


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
            duration=timedelta(days=0, hours=1, minutes=10),
            file_id=Activity.objects.first())  # Should not raise
        self.stat.save()

    def test_get_start_time_returns_time(self):
        self.assertEqual(time(22, 37, 54), self.stat.start_time)

    def test_get_end_time_returns_correct_time(self):
        self.assertEqual(time(22, 37, 57), self.stat.end_time)

    def test_get_end_date_returns_date(self):
        self.assertEqual(date(2014, 7, 15), self.stat.date)

    def test_get_model_max_speed_is_initially_null(self):
        self.assertEqual(None, self.stat.model_max_speed)

    # TODO This test is very slow, definitely need to mock somehow 
    def test_get_model_max_speed_is_populated_on_call_to_max_speed(self):
        self.assertEqual('6.65 knots', self.stat.max_speed)
        self.assertEqual(3.42, self.stat.model_max_speed)

    def test_get_model_max_speed_is_not_pupulated_if_already_filled(self):
        self.stat.model_max_speed = 10.5
        self.stat.save()
        self.assertEqual('20.41 knots', self.stat.max_speed)

    def test_get_model_distance_is_populated_on_call_to_distance(self):
        self.assertEqual('0.01 nmi', self.stat.distance)
        self.assertAlmostEqual(9.9789472033, self.stat.model_distance)


class ActivityModelsIntegrationTests(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_deleting_activity_removes_activity_details(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            Activity.objects.create(
                upfile=SimpleUploadedFile('test1.sbn', SBN_BIN)
            )

            ActivityDetail.objects.create(
                name='',
                file_id=Activity.objects.first())  

            self.assertEqual(1, len(ActivityDetail.objects.all()))
            Activity.objects.first().delete()
            self.assertEqual(0, len(ActivityDetail.objects.all()))

