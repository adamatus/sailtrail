from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

# from unittest.mock import patch, Mock
import unittest

import pytest

import shutil
import tempfile
import os.path

from datetime import datetime, time, date
from pytz import timezone

from activities.models import (Activity, ActivityTrack, ActivityDetail,
                               ActivityStat, ActivityTrackpoint)

from .factories import UserFactory, ActivityFactory, ActivityTrackFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__),
                          'assets')
with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()
    SBN_FILE = SimpleUploadedFile('test1.sbn', SBN_BIN)
with open(os.path.join(ASSET_PATH, 'tiny-run.gpx'), 'rb') as f:
    GPX_BIN = f.read()
    GPX_FILE = SimpleUploadedFile('tiny-run.gpx', GPX_BIN)


@unittest.skip
class ActivityModelTest(TestCase):

    def test_fields_exist_as_expected(self):
        """should have the correct fields"""

        a = Activity(user=UserFactory.create())
        a.save()
        self.assertIsNotNone(a.modified)
        self.assertIsNotNone(a.created)


@pytest.fixture(scope="module")
def sample_activity():
    return

@pytest.mark.django_db
class TestActivityTrackModel:

    def test_model_ordering_on_dates_with_most_last_first(self):
        """should order activites with most recent first"""
        files = ['test{}.sbn'.format(x) for x in [1, 2, 3]]
        hours = [11, 10, 12]
        test_files = []
        for f, t in zip(files, hours):
            test_files.append(SimpleUploadedFile(f, SBN_BIN))
            a = ActivityTrack.create_new(test_files[-1], ActivityFactory.create())

            a.trim_start = datetime(2014, 10, 12, t, 20, 15,
                                    tzinfo=timezone('UTC'))
            a.save()

        activities = ActivityTrack.objects.all()
        assert 'test3.sbn' == activities[2].original_filename
        assert 'test1.sbn' == activities[1].original_filename
        assert 'test2.sbn' == activities[0].original_filename

    def test_empty_trim_should_do_nothing(self):
        """[trim] should do nothing if no times are passed"""
        activity = ActivityFactory.create()
        a = ActivityTrack.create_new(activity_id=activity,
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                      tzinfo=timezone('UTC'))
        a.trim()
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                      tzinfo=timezone('UTC'))

    def test_trim_with_only_start_should_trim_start(self):
        """[trim] should trim start with only trim_start"""
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        a.trim(trim_start="2014-07-15T22:37:55+0000")
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                      tzinfo=timezone('UTC'))

    def test_trim_with_only_end_should_trim_end(self):
        """[trim] should trim end with only trim_end"""
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        a.trim(trim_end="2014-07-15T22:37:56+0000")
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                      tzinfo=timezone('UTC'))

    def test_trim_with_both_should_trim_both(self):
        """[trim] should trim both with only trim_both"""
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        a.trim(trim_start="2014-07-15T22:37:55+0000",
               trim_end="2014-07-15T22:37:56+0000")
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                      tzinfo=timezone('UTC'))

    def test_trim_with_end_before_start_should_flip_and_trim(self):
        """[trim] should flip and trim with start after end"""
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        a.trim(trim_start="2014-07-15T22:37:56+0000",
               trim_end="2014-07-15T22:37:55+0000")
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                                 tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_bad_input_should_gracefully_ignore(self):
        """[trim] should gracefully ignore bad input"""
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        a.trim(trim_start='aa', trim_end='1995')
        assert a.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                        tzinfo=timezone('UTC'))
        assert a.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                      tzinfo=timezone('UTC'))


class ActivitydetailsModelTest(TestCase):

    def setUp(self):
        self.activity = ActivityFactory.create()

    def test_smoke_model_has_expected_fields(self):
        """should have the expected fields"""
        name = 'Test name'
        desc = 'Test description'

        ActivityDetail.objects.create(
            name=name,
            description=desc,
            activity_id=self.activity)  # Should not raise

    def test_cannot_associate_two_details_with_one_file(self):
        """[save] should not allow one file to have multiple details"""
        ActivityDetail.objects.create(
            name='Test', activity_id=self.activity)
        self.assertRaises(
            IntegrityError,
            lambda:
                ActivityDetail.objects.create(
                    name='Test2', activity_id=self.activity)
        )

    def test_cannot_create_details_without_activity_ref(self):
        """[save] should throw if missing a activity_id"""
        self.assertRaises(
            IntegrityError,
            lambda:
                ActivityDetail.objects.create(
                    name='Test')
        )

    def test_cannot_create_details_without_name(self):
        """[save] should throw if missing a name"""
        with self.assertRaises(ValidationError):
            a = ActivityDetail.objects.create(
                activity_id=self.activity)
            a.full_clean()


class ActivitystatModelTest(TestCase):

    def setUp(self):
        a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
            upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        self.stat = a.activity_id.stats

    def test_get_start_time_returns_time(self):
        """[start_time] should return correct time"""
        self.assertEqual(time(22, 37, 54), self.stat.start_time)

    def test_get_end_time_returns_correct_time(self):
        """[end_time] should return correct time"""
        self.assertEqual(time(22, 37, 57), self.stat.end_time)

    def test_get_date_returns_date(self):
        """[date] should return correct date"""
        self.assertEqual(date(2014, 7, 15), self.stat.date)

    def test_get_model_max_speed_is_populated_on_call_to_max_speed(self):
        """[max_speed] should populate model_max_speed if null"""
        self.assertEqual('6.65 knots', self.stat.max_speed)
        self.assertEqual(3.42, self.stat.model_max_speed)

    def test_get_model_max_speed_is_not_pupulated_if_already_filled(self):
        """[max_speed] should not populate model_max_speed if populated"""
        self.stat.model_max_speed = 10.5
        self.stat.save()
        self.assertEqual('20.41 knots', self.stat.max_speed)

    def test_get_model_distance_is_populated_on_call_to_distance(self):
        """[distance] should populate model_distance"""
        self.assertEqual('0.01 nmi', self.stat.distance)
        self.assertAlmostEqual(9.9789472033, self.stat.model_distance)


@unittest.skip
class IntegrationOfActivityModelsTest(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.user = UserFactory.create()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_deleting_activity_removes_activity_details(self):
        """should delete activity details on activity delete"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            activity = Activity.objects.create(user=self.user)

            ActivityDetail.objects.create(
                name='',
                activity_id=activity)

            self.assertEqual(1, len(ActivityDetail.objects.all()))
            activity.delete()
            self.assertEqual(0, len(ActivityDetail.objects.all()))

    def test_integration_upload_sbn_creates_trackpoints(self):
        """should create trackpoints on SBN file upload"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)
            self.assertEquals(0, len(ActivityTrackpoint.objects.all()))
            ActivityTrack.objects.create(
                upfile=test_file,
                activity_id=Activity.objects.create(user=self.user))
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

    def test_integration_upload_gpx_creates_trackpoints(self):
        """should create trackpoints on GPX file upload"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.gpx', GPX_BIN)
            self.assertEquals(0, len(ActivityTrackpoint.objects.all()))
            ActivityTrack.objects.create(
                upfile=test_file,
                activity_id=Activity.objects.create(user=self.user))
            self.assertEquals(5, len(ActivityTrackpoint.objects.all()))
            first = ActivityTrackpoint.objects.first()
            last = ActivityTrackpoint.objects.last()
            self.assertAlmostEquals(43.078269029, first.lat)
            self.assertAlmostEquals(-89.384035754, first.lon)
            self.assertAlmostEquals(0.0, first.sog)
            self.assertEquals(3, first.timepoint.month)
            self.assertEquals(16, first.timepoint.day)
            self.assertEquals(17, first.timepoint.hour)
            self.assertEquals(56, first.timepoint.second)
            self.assertAlmostEquals(43.074852188, last.lat)
            self.assertAlmostEquals(-89.380430865, last.lon)
            self.assertAlmostEquals(2.847290744, last.sog)
            self.assertEquals(3, last.timepoint.month)
            self.assertEquals(16, last.timepoint.day)
            self.assertEquals(17, last.timepoint.hour)
            self.assertEquals(57, last.timepoint.second)

    def test_integration_get_trackpoints_returns_points(self):
        """[get_trackpoints] should return trackpoints"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = ActivityTrack.objects.create(
                upfile=test_file1,
                activity_id=Activity.objects.create(user=self.user))
            tps = a.get_trackpoints()
            self.assertEquals(4, len(tps))
            self.assertAlmostEquals(1, tps[0].id)
            self.assertAlmostEquals(4, tps[3].id)

    def test_integration_get_trackpoints_returns_points_with_start_time(self):
        """[get_trackpoints] should trim to only start_time"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = ActivityTrack.objects.create(
                upfile=test_file1,
                activity_id=Activity.objects.create(user=self.user))
            a.trim_start = datetime(2014, 7, 15, 22, 37, 55,
                                    tzinfo=timezone('UTC'))
            a.save()
            tps = a.get_trackpoints()
            self.assertEquals(3, len(tps))
            self.assertAlmostEquals(2, tps[0].id)
            self.assertAlmostEquals(4, tps[2].id)

    def test_integration_get_trackpoints_returns_points_with_end_time(self):
        """[get_trackpoints] should trim to only end_time"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = ActivityTrack.objects.create(
                upfile=test_file1,
                activity_id=Activity.objects.create(user=self.user))
            a.trim_end = datetime(2014, 7, 15, 22, 37, 56,
                                  tzinfo=timezone('UTC'))
            a.save()
            tps = a.get_trackpoints()
            self.assertEquals(3, len(tps))
            self.assertAlmostEquals(1, tps[0].id)
            self.assertAlmostEquals(3, tps[2].id)

    def test_integration_get_trackpoints_returns_points_with_both_time(self):
        """[get_trackpoints] should trim to both start_time and end_time"""
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file1 = SimpleUploadedFile('test1.sbn', SBN_BIN)
            a = ActivityTrack(upfile=test_file1,
                              activity_id=Activity.objects.create(
                                  user=self.user))
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
