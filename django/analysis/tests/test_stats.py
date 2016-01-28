from datetime import date, time, timedelta, datetime

import pytest
import pytz

from analysis.stats import Stats
from gps import sirf
from tests.assets import get_test_file_path

# Read in the points for the testfile
from tests.utils import my_round

d = sirf.read_sbn(get_test_file_path('test-small.sbn'))
d = [x for x in d.pktq if x is not None]  # filter out Nones

trackpoints = []
app = trackpoints.append  # cache append method for speed
for tp in d:
    app(dict(lat=tp['latitude'],
        lon=tp['longitude'],
        sog=tp['sog'],
        timepoint=datetime.strptime('{} {}'.format(
            tp['time'], tp['date']),
            '%H:%M:%S %Y/%m/%d').replace(tzinfo=pytz.UTC)))


@pytest.fixture(scope="module")
def stats():
    return Stats(trackpoints)


class TestStats:

    def test_get_start_time(self, stats):
        assert time(2, 45, 13) == stats.start_time

    def test_get_end_time(self, stats):
        assert time(2, 45, 40) == stats.end_time

    def test_get_start_date(self, stats):
        assert date(2014, 9, 28) == stats.start_date

    def test_get_duration(self, stats):
        assert timedelta(0, 27) == stats.duration

    def test_get_speeds(self, stats):
        speeds = stats.speeds
        assert 28 == len(speeds)
        assert 2.19 == speeds[0].magnitude

    def test_get_max_speed(self, stats):
        assert '2.53 m / s' == '{:~}'.format(stats.max_speed)

    def test_get_distance_haversine_method(self, stats):
        assert 59.125 == my_round(stats.distance(method='Haversine').magnitude)

    def test_get_distance_sphlawcos_method(self, stats):
        assert 59.114 == my_round(stats.distance(method='SphLawCos').magnitude)

    def test_get_distance_equirect_method(self, stats):
        assert 59.125 == my_round(stats.distance(method='Equirect').magnitude)

    def test_get_bearing(self, stats):
        bearings = stats.bearing()
        assert 27 == len(bearings)
        assert 240.084 == my_round(bearings[0])
        assert 249.443 == my_round(bearings[26])
