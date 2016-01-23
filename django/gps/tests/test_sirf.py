import os
from datetime import datetime
from unittest.mock import Mock, sentinel, patch

import pytz

from gps import sirf

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '../../tests/assets')
TEST_FILE = os.path.join(ASSET_DIR, 'test-small.sbn')


class TestSirf:

    def test_reading_of_sirf_file(self):
        p = sirf.read_sbn(os.path.join(ASSET_DIR, 'test.sbn'))
        assert p.counts['rx'] == 679
        assert p.pktq[1]['date'] == '2013/07/09'
        assert p.pktq[1]['time'] == '23:54:47'
        assert p.pktq[1]['fixtype'] == '4+-SV KF'
        assert p.pktq[1]['latitude'] == 43.0771931
        assert p.pktq[1]['longitude'] == -89.4007119
        assert p.pktq[620]['date'] == '2013/07/10'
        assert p.pktq[620]['time'] == '00:05:00'
        assert p.pktq[620]['fixtype'] == '4+-SV KF'
        assert p.pktq[620]['latitude'] == 43.0771587
        assert p.pktq[620]['longitude'] == -89.4006786


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
