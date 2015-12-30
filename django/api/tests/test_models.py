from datetime import datetime, time, date
import os.path
import shutil
import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from pytz import timezone

from api.models import (Activity, ActivityTrack,
                        ActivityTrackpoint, _create_trackpoints)
from api.tests.factories import ActivityFactory
from users.tests.factories import UserFactory

ASSET_PATH = os.path.join(os.path.dirname(__file__),
                          'assets')
with open(os.path.join(ASSET_PATH, 'tiny.SBN'), 'rb') as f:
    SBN_BIN = f.read()
    SBN_FILE = SimpleUploadedFile('test1.sbn', SBN_BIN)
with open(os.path.join(ASSET_PATH, 'tiny-run.gpx'), 'rb') as f:
    GPX_BIN = f.read()
    GPX_FILE = SimpleUploadedFile('tiny-run.gpx', GPX_BIN)


def my_round(num, places=3):
    return int(num*10**places)/10**places


class FileDeleter:
    def setUp(self):
        print('in deleter')
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


@pytest.mark.django_db
@pytest.mark.integration
class TestActivityModelIntegration(FileDeleter, TestCase):

    def setUp(self):
        super(TestActivityModelIntegration, self).setUp()
        with self.settings(MEDIA_ROOT=self.temp_dir):
            a = ActivityTrack.create_new(activity_id=ActivityFactory.create(),
                                         upfile=SimpleUploadedFile("test1.SBN",
                                                                   SBN_BIN))
        self.activity = a.activity_id  # type: Activity

    def test_fields_exist_as_expected(self):
        a = Activity(user=UserFactory.create())
        a.save()
        assert a.modified is not None
        assert a.created is not None

    def test_start_time_returns_time(self):
        assert self.activity.start_time == time(22, 37, 54)

    def test_end_time_returns_correct_time(self):
        assert self.activity.end_time == time(22, 37, 57)

    def test_date_returns_date(self):
        assert self.activity.date == date(2014, 7, 15)

    def test_model_max_speed_is_populated_on_call_to_max_speed(self):
        self.activity.model_max_speed = None
        self.activity.save()
        assert self.activity.max_speed == '6.65 knots'
        assert self.activity.model_max_speed == 3.42

    def test_model_max_speed_is_not_pupulated_if_already_filled(self):
        self.activity.model_max_speed = 10.5
        self.activity.save()
        assert self.activity.max_speed == '20.41 knots'
        assert self.activity.model_max_speed == 10.5

    def test_model_distance_is_populated_on_call_to_distance(self):
        self.activity.model_distance = None
        self.activity.save()
        assert self.activity.distance == '0.01 nmi'
        assert my_round(self.activity.model_distance) == 9.978

    def test_model_distance_is_not_populated_if_already_filled(self):
        self.activity.model_distance = 10.5
        self.activity.save()
        assert self.activity.distance == '0.01 nmi'
        assert my_round(self.activity.model_distance) == 10.5


@pytest.mark.django_db
@pytest.mark.integration
class TestActivityTrackModelIntegration(FileDeleter, TestCase):

    def setUp(self):
        super(TestActivityTrackModelIntegration, self).setUp()

        def make_track():
            with self.settings(MEDIA_ROOT=self.temp_dir):
                self.track = ActivityTrack.create_new(
                    activity_id=ActivityFactory.create(),
                    upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        self.make_track = make_track

    def test_model_ordering_on_dates_with_most_last_first(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            files = ['test{}.sbn'.format(x) for x in [1, 2, 3]]
            hours = [11, 10, 12]
            test_files = []
            for f, t in zip(files, hours):
                test_files.append(SimpleUploadedFile(f, SBN_BIN))
                a = ActivityTrack.create_new(test_files[-1],
                                             ActivityFactory.create())

                a.trim_start = datetime(2014, 10, 12, t, 20, 15,
                                        tzinfo=timezone('UTC'))
                a.save()

            activities = ActivityTrack.objects.all()
            assert 'test3.sbn' == activities[2].original_filename
            assert 'test1.sbn' == activities[1].original_filename
            assert 'test2.sbn' == activities[0].original_filename

    def test_empty_trim_should_do_nothing(self):
        self.make_track()
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                               tzinfo=timezone('UTC'))

        self.track.trim()
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_only_start_should_trim_start(self):
        self.make_track()
        self.track.trim(trim_start="2014-07-15T22:37:55+0000")
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_only_end_should_trim_end(self):
        self.make_track()
        self.track.trim(trim_end="2014-07-15T22:37:56+0000")
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_both_should_trim_both(self):
        self.make_track()
        self.track.trim(trim_start="2014-07-15T22:37:55+0000",
                        trim_end="2014-07-15T22:37:56+0000")
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_end_before_start_should_flip_and_trim(self):
        self.make_track()
        self.track.trim(trim_start="2014-07-15T22:37:56+0000",
                        trim_end="2014-07-15T22:37:55+0000")
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 55,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 56,
                                               tzinfo=timezone('UTC'))

    def test_trim_with_bad_input_should_gracefully_ignore(self):
        self.make_track()
        self.track.trim(trim_start='aa', trim_end='1995')
        assert self.track.trim_start == datetime(2014, 7, 15, 22, 37, 54,
                                                 tzinfo=timezone('UTC'))
        assert self.track.trim_end == datetime(2014, 7, 15, 22, 37, 57,
                                               tzinfo=timezone('UTC'))

    def test_create_trackpoints_will_call_sbn_helper(self):
        bad_file = SimpleUploadedFile('tiny-run.tpx', GPX_BIN)
        with pytest.raises(Exception):
            _create_trackpoints(None, bad_file)


@pytest.mark.django_db
@pytest.mark.integration
class TestIntegrationOfActivityModelsIntegration(FileDeleter, TestCase):

    def setUp(self):
        super(TestIntegrationOfActivityModelsIntegration, self).setUp()

        def make_track():
            with self.settings(MEDIA_ROOT=self.temp_dir):
                self.track = ActivityTrack.create_new(
                    activity_id=ActivityFactory.create(),
                    upfile=SimpleUploadedFile("test1.SBN", SBN_BIN))
        self.make_track = make_track

    def test_upload_sbn_creates_trackpoints(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.sbn', SBN_BIN)
            assert 0 == len(ActivityTrackpoint.objects.all())

            ActivityTrack.create_new(
                upfile=test_file,
                activity_id=Activity.objects.create(user=UserFactory.create()))

            assert 4 == len(ActivityTrackpoint.objects.all())

            first = ActivityTrackpoint.objects.first()
            last = ActivityTrackpoint.objects.last()

            assert my_round(first.lat) == 43.087
            assert my_round(first.lon) == -89.389
            assert my_round(first.sog) == 3.11
            assert first.timepoint.month == 7
            assert first.timepoint.day == 15
            assert first.timepoint.hour == 22
            assert first.timepoint.second == 54
            assert my_round(last.lat) == 43.087
            assert my_round(last.lon) == -89.389
            assert my_round(last.sog) == 3.420
            assert last.timepoint.month == 7
            assert last.timepoint.day == 15
            assert last.timepoint.hour == 22
            assert last.timepoint.second == 57

    def test_upload_gpx_creates_trackpoints(self):
        with self.settings(MEDIA_ROOT=self.temp_dir):
            test_file = SimpleUploadedFile('test1.gpx', GPX_BIN)
            assert len(ActivityTrackpoint.objects.all()) == 0

            ActivityTrack.create_new(
                upfile=test_file,
                activity_id=Activity.objects.create(user=UserFactory.create()))
            assert len(ActivityTrackpoint.objects.all()) == 5

            first = ActivityTrackpoint.objects.first()
            last = ActivityTrackpoint.objects.last()

            assert my_round(first.lat) == 43.078
            assert my_round(first.lon) == -89.384
            assert first.sog == 0.0
            assert first.timepoint.month == 3
            assert first.timepoint.day == 16
            assert first.timepoint.hour == 17
            assert first.timepoint.second == 56

            assert my_round(last.lat) == 43.074
            assert my_round(last.lon) == -89.380
            assert my_round(last.sog) == 2.847
            assert last.timepoint.month == 3
            assert last.timepoint.day == 16
            assert last.timepoint.hour == 17
            assert last.timepoint.second == 57

    def test_get_trackpoints_returns_points(self):
        self.make_track()
        tps = self.track.get_trackpoints()
        assert len(tps) == 4
        assert tps[0].id == 1
        assert tps[3].id == 4

    def test_get_trackpoints_returns_points_with_start_time(self):
        self.make_track()
        self.track.trim_start = datetime(2014, 7, 15, 22, 37, 55,
                                         tzinfo=timezone('UTC'))
        self.track.save()
        tps = self.track.get_trackpoints()
        assert len(tps) == 3
        assert tps[0].id == 2
        assert tps[2].id == 4

    def test_get_trackpoints_returns_points_with_end_time(self):
        self.make_track()
        self.track.trim_end = datetime(2014, 7, 15, 22, 37, 56,
                                       tzinfo=timezone('UTC'))
        self.track.save()
        tps = self.track.get_trackpoints()
        assert len(tps) == 3
        assert tps[0].id == 1
        assert tps[2].id == 3

    def test_integration_get_trackpoints_returns_points_with_both_time(self):
        self.make_track()
        self.track.save()
        self.track.trim_start = datetime(2014, 7, 15, 22, 37, 55,
                                         tzinfo=timezone('UTC'))
        self.track.trim_end = datetime(2014, 7, 15, 22, 37, 56,
                                       tzinfo=timezone('UTC'))
        self.track.save()
        tps = self.track.get_trackpoints()
        assert len(tps) == 2
        assert tps[0].id == 2
        assert tps[1].id == 3
