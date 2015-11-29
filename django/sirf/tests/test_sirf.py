import os
from datetime import date, time, timedelta, datetime

import pytest
import pytz

import sirf
from sirf.stats import Stats


ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'assets')
TEST_FILE = os.path.join(ASSET_DIR, 'test-small.sbn')

# Read in the points for the testfile
d = sirf.read_sbn(TEST_FILE)
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


@pytest.fixture(scope="module")
def stats():
    return Stats(trackpoints)


def my_round(number):
    return int(number*1000)/1000


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
