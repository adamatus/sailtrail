from datetime import datetime
from unittest.mock import MagicMock, patch, sentinel, Mock

import pytest
import pytz
from django.core.exceptions import SuspiciousOperation

from api.models import Activity, ActivityTrack, track_upload_path, \
    ActivityTrackFile, ActivityTrackpoint


class TestActivityModel:

    @patch('api.models.reverse')
    def test_get_absolute_url_returns_result_of_reverse(self,
                                                        rev_mock: MagicMock):
        # Given a new activity
        activity = Activity()
        activity.id = sentinel.id

        rev_mock.return_value = sentinel.url

        # When getting the absolute url
        url = activity.get_absolute_url()

        # Then the sentinel is returned
        assert url == sentinel.url
        rev_mock.assert_called_once_with('view_activity',
                                         args=[str(sentinel.id)])

    def test_start_time(self):
        # Given a track mock that return trim_start time from first track
        track_mock = Mock()
        track_mock.return_value.first.return_value.trim_start.\
            time.return_value = sentinel.time

        # and and activity with that mock
        activity = Activity()
        activity._get_tracks = track_mock

        # Then the sentinel time is returned
        assert activity.start_time == sentinel.time

    def test_end_time(self):
        # Given a track mock that return trim_end time from last track
        track_mock = Mock()
        track_mock.return_value.last.return_value.trim_end. \
            time.return_value = sentinel.time

        # and and activity with that mock
        activity = Activity()
        activity._get_tracks = track_mock

        # Then the sentinel time is returned
        assert activity.end_time == sentinel.time

    def test_date(self):
        # Given a track mock that return trim_start time from first track
        track_mock = Mock()
        track_mock.return_value.first.return_value.trim_start. \
            date.return_value = sentinel.date

        # and and activity with that mock
        activity = Activity()
        activity._get_tracks = track_mock

        # Then the sentinel time is returned
        assert activity.date == sentinel.date

    def test_duration(self):
        # Given a track mock that return trim_start time from first track
        track_mock = Mock()
        track_mock.return_value.first.return_value.trim_start = 8
        track_mock.return_value.last.return_value.trim_end = 10

        # and and activity with that mock
        activity = Activity()
        activity._get_tracks = track_mock

        # Then the sentinel time is returned
        assert activity.duration == 2

    def test_max_speed_returns_existing_formatted_model_max_speed(self):
        # Given a new activity with max speed
        activity = Activity()
        activity.model_max_speed = 10.0

        # Expect the property to be a formatted speed string
        assert activity.max_speed == "19.44 knots"

    @patch('api.models.Stats')
    def test_max_speed_property_computes_and_saves(self,
                                                   stats_mock: MagicMock):
        # Given a new activity and some mocks
        activity = Activity()
        activity.get_trackpoints = Mock(return_value=sentinel.pos)
        stats_mock.return_value.max_speed.magnitude = 10
        activity.save = Mock()

        # When getting the max speed
        max_speed = activity.max_speed

        # Then the property returns a formatted speed string
        assert max_speed == "19.44 knots"
        assert activity.max_speed == "19.44 knots"  # get again

        # and mocks were only called once
        stats_mock.assert_called_once_with(sentinel.pos)
        activity.get_trackpoints.assert_called_once_with()
        activity.save.assert_called_once_with()

    def test_distance_returns_existing_formatted_distance(self):
        # Given a new activity with distance
        activity = Activity()
        activity.model_distance = 100.0

        # Expect the property to be a formatted distance string
        assert activity.distance == "0.05 nmi"

    @patch('api.models.Stats')
    def test_distance_property_computes_and_saves(self,
                                                  stats_mock: MagicMock):
        # Given a new activity and some mocks
        activity = Activity()
        activity.get_trackpoints = Mock(return_value=sentinel.pos)
        stats_mock.return_value.distance.return_value.magnitude = 100
        activity.save = Mock()

        # When getting the max speed
        distance = activity.distance

        # Then the property returns a formatted speed string
        assert distance == "0.05 nmi"
        assert activity.distance == "0.05 nmi"  # get again

        # and mocks were only called once
        stats_mock.assert_called_once_with(sentinel.pos)
        activity.get_trackpoints.assert_called_once_with()
        activity.save.assert_called_once_with()

    @patch('api.models.Stats')
    def test_compute_stats_populates_model_fields(self,
                                                  stats_mock: MagicMock):
        # Given a new activity with some mocks
        activity = Activity()
        activity.get_trackpoints = Mock(return_value=sentinel.pos)
        activity.save = Mock()
        computed_stats = Mock()
        stats_mock.return_value = computed_stats
        computed_stats.distance.return_value.magnitude = sentinel.dist
        computed_stats.max_speed.magnitude = sentinel.max_speed

        # When computing stats
        activity.compute_stats()

        # Then the values were set as expected, after mock calls
        assert activity.model_distance == sentinel.dist
        assert activity.model_max_speed == sentinel.max_speed
        stats_mock.assert_called_once_with(sentinel.pos)
        activity.save.assert_called_once_with()

    @patch("api.models.ActivityTrack")
    def test_add_track_creates_new(self, track_mock: MagicMock):
        # Given a new activity
        activity = Activity()

        # When adding a track
        activity.add_track(sentinel.file)

        # Then mock was called
        track_mock.create_new.assert_called_once_with(sentinel.file, activity)

    def test_get_trackpoints(self):
        # Given some track mocks
        tracks_mock = Mock()
        track1_mock = Mock()
        track2_mock = Mock()
        tracks_mock.return_value.all.return_value.order_by.return_value = [
            track1_mock, track2_mock
        ]
        track1_mock.get_trackpoints.return_value.values.return_value = [1, 2]
        track2_mock.get_trackpoints.return_value.values.return_value = \
            [3, 4, 5]

        # and an activity that returns those mocks
        activity = Activity()
        activity._get_tracks = tracks_mock

        # When getting the trackpoints
        trackpoints = activity.get_trackpoints()

        # Then the track data is returned
        assert len(trackpoints) == 5
        assert trackpoints == [1, 2, 3, 4, 5]

        # and mocks were called correctly
        tracks_mock.return_value.all.return_value.order_by.\
            assert_called_once_with('trim_start')
        track1_mock.get_trackpoints.return_value.\
            values.assert_called_once_with('sog', 'lat', 'lon', 'timepoint')
        track2_mock.get_trackpoints.return_value.\
            values.assert_called_once_with('sog', 'lat', 'lon', 'timepoint')


class TestActivityTrackModel:

    def test_str_produces_pretty_output(self):
        track = ActivityTrack()
        file = Mock()
        file.file.name = "TestFile.sbn"
        track._get_original_file = Mock(return_value=file)

        str_rep = track.__str__()

        assert str_rep == "ActivityTrack (TestFile.sbn)"

    def test_initialize_stats_sets_datetime(self):
        track = ActivityTrack()
        activity = Mock()
        activity.datetime = None

        track.trim_start = sentinel.trim_start
        track.reset_trim = Mock()
        track._get_activity = Mock(return_value=activity)

        # When initializing stats
        track.initialize_stats()

        # Then mocks were called correctly
        track.reset_trim.assert_called_once_with()
        assert activity.datetime == sentinel.trim_start
        activity.save.assert_called_once_with()

    def test_initialize_stats_resets_datetime(self):
        track = ActivityTrack()
        activity = Mock()
        activity.datetime = datetime(2015, 2, 1)

        track.trim_start = datetime(2015, 1, 1)
        track.reset_trim = Mock()
        track._get_activity = Mock(return_value=activity)

        # When initializing stats
        track.initialize_stats()

        # Then mocks were called correctly
        track.reset_trim.assert_called_once_with()
        assert activity.datetime == datetime(2015, 1, 1)
        activity.save.assert_called_once_with()

    def test_initialize_stats_does_nothing_with_earlier_activity(self):
        track = ActivityTrack()
        activity = Mock()
        activity.datetime = datetime(2015, 1, 1)

        track.trim_start = datetime(2015, 2, 1)
        track.reset_trim = Mock()
        track._get_activity = Mock(return_value=activity)

        # When initializing stats
        track.initialize_stats()

        # Then mocks were called correctly
        track.reset_trim.assert_called_once_with()
        assert activity.datetime == datetime(2015, 1, 1)
        activity.save.assert_not_called()

    def test_trim_does_nothing_with_no_input(self):
        track = ActivityTrack()
        track.save = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)

        track.trim()

        assert track.trimmed is False
        assert track.trim_start == datetime(2015, 1, 1, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track.save.assert_not_called()

    def test_trim_with_reasonable_trim_start_sets_it(self):
        track = ActivityTrack()
        track.save = Mock()
        track._get_activity = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track._get_limits = Mock(return_value=(
            datetime(2014, 1, 1, tzinfo=pytz.UTC),
            datetime(2016, 1, 4, tzinfo=pytz.UTC)
        ))

        track.trim(trim_start="2015-01-02T00:00:00+0000")

        assert track.trim_start == datetime(2015, 1, 2, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 4, tzinfo=pytz.UTC)
        assert track.trimmed is True
        track.save.assert_called_once_with()
        track._get_activity.return_value.\
            compute_stats.assert_called_once_with()

    def test_trim_with_reasonable_trim_end_sets_it(self):
        track = ActivityTrack()
        track.save = Mock()
        track._get_activity = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track._get_limits = Mock(return_value=(
            datetime(2014, 1, 1, tzinfo=pytz.UTC),
            datetime(2016, 1, 4, tzinfo=pytz.UTC)
        ))

        track.trim(trim_end="2015-01-02T00:00:00+0000")

        assert track.trim_start == datetime(2015, 1, 1, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 2, tzinfo=pytz.UTC)
        assert track.trimmed is True
        track.save.assert_called_once_with()
        track._get_activity.return_value.\
            compute_stats.assert_called_once_with()

    def test_trim_with_reasonable_trim_start_and_end_sets_them(self):
        track = ActivityTrack()
        track.save = Mock()
        track._get_activity = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track._get_limits = Mock(return_value=(
            datetime(2014, 1, 1, tzinfo=pytz.UTC),
            datetime(2016, 1, 4, tzinfo=pytz.UTC)
        ))

        track.trim(trim_start="2015-01-02T00:00:00+0000",
                   trim_end="2015-01-03T00:00:00+0000")

        assert track.trim_start == datetime(2015, 1, 2, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 3, tzinfo=pytz.UTC)
        assert track.trimmed is True
        track.save.assert_called_once_with()
        track._get_activity.return_value.\
            compute_stats.assert_called_once_with()

    def test_trim_with_flipped_trim_start_and_end_sets_them(self):
        track = ActivityTrack()
        track.save = Mock()
        track._get_activity = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track._get_limits = Mock(return_value=(
            datetime(2014, 1, 1, tzinfo=pytz.UTC),
            datetime(2016, 1, 4, tzinfo=pytz.UTC)
        ))

        track.trim(trim_start="2015-01-03T00:00:00+0000",
                   trim_end="2015-01-02T00:00:00+0000")

        assert track.trim_start == datetime(2015, 1, 2, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 3, tzinfo=pytz.UTC)
        assert track.trimmed is True
        track.save.assert_called_once_with()
        track._get_activity.return_value.\
            compute_stats.assert_called_once_with()

    def test_trim_does_nothing_with_junk_input(self):
        track = ActivityTrack()
        track.save = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)

        track.trim(trim_start="TRIM CRAZY",
                   trim_end="CRAZYNESS")

        assert track.trimmed is False
        assert track.trim_start == datetime(2015, 1, 1, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 4, tzinfo=pytz.UTC)
        track.save.assert_not_called()

    def test_trim_raises_bad_request_if_start_and_end_equal(self):
        track = ActivityTrack()
        track.save = Mock()
        track.trim_start = datetime(2015, 1, 1, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 4, tzinfo=pytz.UTC)

        with pytest.raises(SuspiciousOperation):
            track.trim(trim_start="2015-01-02T00:00:00+0000",
                       trim_end="2015-01-02T00:00:00+0000")

    def test_trim_with_out_of_rance_trim_start_and_end_sets_them_to_lim(self):
        track = ActivityTrack()
        track.save = Mock()
        track._get_activity = Mock()
        track.trim_start = datetime(2015, 1, 2, tzinfo=pytz.UTC)
        track.trim_end = datetime(2015, 1, 3, tzinfo=pytz.UTC)
        track._get_limits = Mock(return_value=(
            datetime(2015, 1, 1, tzinfo=pytz.UTC),
            datetime(2015, 1, 4, tzinfo=pytz.UTC)
        ))

        track.trim(trim_start="2014-01-03T00:00:00+0000",
                   trim_end="2016-01-02T00:00:00+0000")

        assert track.trim_start == datetime(2015, 1, 1, tzinfo=pytz.UTC)
        assert track.trim_end == datetime(2015, 1, 4, tzinfo=pytz.UTC)
        assert track.trimmed is True
        track.save.assert_called_once_with()
        track._get_activity.return_value. \
            compute_stats.assert_called_once_with()

    def test_reset_trim_resets_the_trim(self):
        track = ActivityTrack()

        track._get_limits = Mock(return_value=(sentinel.start, sentinel.end))
        track.save = Mock()
        track._get_activity = Mock()

        track.reset_trim()

        assert track.trimmed is False
        assert track.trim_start == sentinel.start
        assert track.trim_end == sentinel.end
        track.save.assert_called_once_with()

    def test_get_limits_returns_trackpoint_limits(self):
        track = ActivityTrack()
        trackpoint = Mock()
        trackpoint.first.return_value.timepoint = sentinel.start
        trackpoint.last.return_value.timepoint = sentinel.end
        track._get_trackpoints = Mock(return_value=trackpoint)

        start, end = track._get_limits()

        assert start == sentinel.start
        assert end == sentinel.end

    def test_get_trackpoints_returns_expected(self):
        track = ActivityTrack()
        track.trim_start = sentinel.start
        track.trim_end = sentinel.end

        trackpoint = Mock()
        trackpoint.filter.return_value.order_by.return_value = sentinel.tps
        track._get_trackpoints = Mock(return_value=trackpoint)

        trackpoints = track.get_trackpoints()

        assert trackpoints == sentinel.tps
        trackpoint.filter.assert_called_once_with(
            timepoint__range=(sentinel.start, sentinel.end)
        )
        trackpoint.filter.return_value.order_by.assert_called_once_with(
            'timepoint'
        )

    @patch('api.models.ActivityTrackpoint')
    @patch('api.models.ActivityTrack.objects')
    @patch('api.models.ActivityTrackFile')
    def test_create_new_creates_new_track_and_file(self,
                                                   track_file_mock,
                                                   obj_mock,
                                                   tps_mock):
        new_track = Mock()
        obj_mock.create.return_value = new_track

        upfile = Mock()
        upfile.name = sentinel.name

        track = ActivityTrack.create_new(upfile, sentinel.id)

        assert track == new_track
        obj_mock.create.assert_called_once_with(
            activity_id=sentinel.id,
            original_filename=sentinel.name
        )
        track_file_mock.objects.create.assert_called_once_with(
            track=new_track,
            file=upfile
        )
        upfile.seek.assert_called_once_with(0)
        tps_mock.create_trackpoints.assert_called_once_with(new_track, upfile)
        new_track.initialize_stats.assert_called_once_with()


class TestActivityTrackFileModel:

    @patch('api.models.uuid')
    def test_track_upload_path_creates_path_with_uuid(self, uuid_mock):

        uuid_mock.uuid4.return_value = '12345'

        path = track_upload_path(None, 'file.ext')

        assert path == 'originals/12345/file.ext'

    def test_str_makes_pretty_string(self):
        track_file = ActivityTrackFile()
        track_file.file = 'filename.txt'

        str_rep = str(track_file)

        assert str_rep == 'ActivityTrackFile (filename.txt)'


class TestActivityTrackpointModel:

    @patch('api.models.sirf')
    @patch('api.models.ActivityTrackpoint.objects')
    def test_creates_sirf_trackpoints_and_saves(self, object_mock, sirf_mock):
        sirf_mock.create_trackpoints.return_value = sentinel.trackpoints

        up_file = Mock()
        up_file.name = 'test.Sbn'

        ActivityTrackpoint.create_trackpoints(sentinel.track, up_file)

        sirf_mock.create_trackpoints.assert_called_once_with(
            sentinel.track, up_file, ActivityTrackpoint
        )
        object_mock.bulk_create.assert_called_once_with(sentinel.trackpoints)

    @patch('api.models.gpx')
    @patch('api.models.ActivityTrackpoint.objects')
    def test_creates_gpx_trackpoints_and_saves(self, object_mock, gpx_mock):
        gpx_mock.create_trackpoints.return_value = sentinel.trackpoints

        up_file = Mock()
        up_file.name = 'test.GPx'

        ActivityTrackpoint.create_trackpoints(sentinel.track, up_file)

        gpx_mock.create_trackpoints.assert_called_once_with(
            sentinel.track, up_file, ActivityTrackpoint
        )
        object_mock.bulk_create.assert_called_once_with(sentinel.trackpoints)

    def test_raises_with_unsupported_filetype(self):
        up_file = Mock()
        up_file.name = 'test.txt'

        with pytest.raises(SuspiciousOperation):
            ActivityTrackpoint.create_trackpoints(sentinel.track, up_file)
