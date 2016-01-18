from datetime import datetime
from unittest.mock import patch, Mock, sentinel

import pytz
from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment, GPXTrack, GPX

from gps.gpx import create_trackpoints


class TestCreateTrackpoints:

    @patch('gps.gpx.gpxpy')
    def test_create_work_as_expected(self, gpxpy_mock):
        # Given some fake GPX data
        pnt1 = GPXTrackPoint(latitude=1,
                             longitude=1,
                             time=datetime(2016, 1, 1))
        pnt2 = GPXTrackPoint(latitude=2,
                             longitude=2,
                             time=datetime(2016, 1, 2))
        segment = GPXTrackSegment(points=[pnt1, pnt2])
        track = GPXTrack()
        track.segments = [segment]
        gpx = GPX()
        gpx.tracks = [track]

        # Given a mock gpxpy that returns the fake data
        gpxpy_mock.parse.return_value = gpx

        trackpoint_mock = Mock()

        up_file = Mock()
        up_file.read.return_value.decode.return_value = sentinel.gpx_raw

        # When creating trackpoints
        tps = create_trackpoints(sentinel.track, up_file, trackpoint_mock)

        # Then the correct stuff happens
        assert len(tps) == 2
        trackpoint_mock.assert_any_call(
            lat=1,
            lon=1,
            sog=0,
            timepoint=datetime(2016, 1, 1, tzinfo=pytz.UTC),
            track=sentinel.track
        )
        trackpoint_mock.assert_any_call(
            lat=2,
            lon=2,
            sog=1.819738796736955,
            timepoint=datetime(2016, 1, 2, tzinfo=pytz.UTC),
            track=sentinel.track
        )

        gpxpy_mock.parse.assert_called_once_with(sentinel.gpx_raw)
        up_file.read.assert_called_once_with()
        up_file.read.return_value.decode.assert_called_once_with('utf-8')
