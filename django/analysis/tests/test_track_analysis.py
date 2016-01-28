import datetime as dt
from unittest.mock import patch, MagicMock, sentinel

import numpy as np

from analysis.track_analysis import make_json_from_trackpoints


class TestMakeJson:

    @patch('analysis.track_analysis.Stats')
    @patch('analysis.track_analysis.np')
    def test_make_json_returns_expected_trackpoint_data(self,
                                                        np_mock: MagicMock,
                                                        stat_mock: MagicMock):
        # Given some fake position data
        pos = [{'lat': 1, 'lon': 11, 'sog': 111,
                'timepoint': dt.datetime(2016, 1, 14, 8, 11, 0)},
               {'lat': 2, 'lon': 22, 'sog': 222,
                'timepoint': dt.datetime(2016, 1, 14, 8, 11, 1)},
               {'lat': 3, 'lon': 33, 'sog': 333,
                'timepoint': dt.datetime(2016, 1, 14, 8, 11, 2)},
               ]

        # and come mocks setup to return meaningful values
        stat_mock.return_value.bearing.return_value = [1, 2]
        np_mock.append.return_value = sentinel.round_me
        np_mock.round.return_value = np.asarray([1111, 2222, 3333])

        # When making json from trackpoints
        json = make_json_from_trackpoints(pos)

        # Then the resulting dict has the expected shape
        assert 'lat' in json
        assert json['lat'] == [1, 2, 3]
        assert 'lon' in json
        assert json['lon'] == [11, 22, 33]
        assert 'speed' in json
        assert json['speed'] == [215.77, 431.53, 647.3]
        assert 'bearing' in json
        assert json['bearing'] == [1111, 2222, 3333]
        assert 'time' in json
        assert json['time'] == ['2016-01-14T08:11:00',
                                '2016-01-14T08:11:01',
                                '2016-01-14T08:11:02']

        # and mocks were called correctly
        stat_mock.assert_called_once_with(pos)
        stat_mock.return_value.bearing.assert_called_once_with()
        np_mock.round.assert_called_once_with(sentinel.round_me)
        np_mock.append.assert_called_once_with([1, 2], 2)
