from datetime import datetime
from unittest.mock import Mock, sentinel, patch

import pytz

from gps import sirf


class TestCreateTrackpoints:

    @patch('gps.sirf.Parser')
    def test_create_work_as_expected(self, parse_mock):
        # Given some fake GPX data
        pnt1 = dict(latitude=1,
                    longitude=1,
                    sog=1,
                    fixtype="good",
                    time='00:00:00',
                    date="2016/01/01")
        pnt2 = dict(latitude=2,
                    longitude=2,
                    sog=2,
                    fixtype="good",
                    time='00:00:00',
                    date="2016/01/02")
        pnt3 = dict(fixtype="none")

        # Given a mock gpxpy that returns the fake data
        parse_mock.return_value = Mock(pktq=[None, pnt1, pnt2, pnt3])

        trackpoint_mock = Mock()

        up_file = Mock()
        up_file.read.return_value = sentinel.sirf_raw

        # When creating trackpoints
        tps = sirf.create_trackpoints(sentinel.track, up_file, trackpoint_mock)

        # Then the correct stuff happens
        assert len(tps) == 2
        trackpoint_mock.assert_any_call(
            lat=1,
            lon=1,
            sog=1,
            timepoint=datetime(2016, 1, 1, tzinfo=pytz.UTC),
            track=sentinel.track
        )
        trackpoint_mock.assert_any_call(
            lat=2,
            lon=2,
            sog=2,
            timepoint=datetime(2016, 1, 2, tzinfo=pytz.UTC),
            track=sentinel.track
        )

        parse_mock.assert_called_once_with()
        parse_mock.return_value.process.assert_called_once_with(
            sentinel.sirf_raw)

        up_file.read.assert_called_once_with()
