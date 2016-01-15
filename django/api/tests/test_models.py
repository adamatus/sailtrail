from unittest.mock import MagicMock, patch, sentinel, Mock

from api.models import Activity


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
