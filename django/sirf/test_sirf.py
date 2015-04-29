import unittest
import os
import sirf
from sirf.stats import Stats

from datetime import date, time, timedelta, datetime
import pytz

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_assets')
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


class SirfTest(unittest.TestCase):

    def test_reading_of_sirf_file(self):
        """[read_sbn] should correctly parse SBN file"""
        p = sirf.read_sbn(os.path.join(ASSET_DIR, 'test.sbn'))
        self.assertEquals(679, p.rx_cnt)
        self.assertEquals('2013/07/09', p.pktq[1]['date'])
        self.assertEquals('23:54:47', p.pktq[1]['time'])
        self.assertEquals('4+-SV KF', p.pktq[1]['fixtype'])
        self.assertAlmostEquals(43.0771931, p.pktq[1]['latitude'])
        self.assertAlmostEquals(-89.4007119, p.pktq[1]['longitude'])
        self.assertEquals('2013/07/10', p.pktq[620]['date'])
        self.assertEquals('00:05:00', p.pktq[620]['time'])
        self.assertEquals('4+-SV KF', p.pktq[620]['fixtype'])
        self.assertAlmostEquals(43.0771587, p.pktq[620]['latitude'])
        self.assertAlmostEquals(-89.4006786, p.pktq[620]['longitude'])


class StatsTest(unittest.TestCase):

    def setUp(self):
        self.stats = Stats(trackpoints)

    def test_get_start_time(self):
        """[start_time] should return correct start time"""
        self.assertEquals(time(2, 45, 13), self.stats.start_time)

    def test_get_end_time(self):
        """[end_time] should return correct end time"""
        self.assertEquals(time(2, 45, 40), self.stats.end_time)

    def test_get_start_date(self):
        """[start_date] should return correct start date"""
        self.assertEquals(date(2014, 9, 28), self.stats.start_date)

    def test_get_duration(self):
        """[duration] should return correct duration"""
        self.assertEquals(timedelta(0, 27), self.stats.duration)

    def test_get_speeds(self):
        """[speeds] should return array of speeds"""
        speeds = self.stats.speeds
        self.assertEquals(28, len(speeds))
        self.assertAlmostEquals(2.19, speeds[0].magnitude)

    def test_get_max_speed(self):
        """[max_speed] should return correct max speed (in m/s)"""
        self.assertEqual('2.53 m / s', '{:~}'.format(self.stats.max_speed))

    def test_get_distance_haversine_method(self):
        """[get_distance] should return correct haversine distance"""
        self.assertAlmostEquals(
            59.12590197, self.stats.distance(method='Haversine').magnitude)

    def test_get_distance_sphlawcos_method(self):
        """[get_distance] should return correct sph. law of cosines distance"""
        self.assertAlmostEquals(
            59.11451088, self.stats.distance(method='SphLawCos').magnitude)

    def test_get_distance_equirect_method(self):
        """[get_distance] should return correct equirect distance"""
        self.assertAlmostEquals(
            59.12590197, self.stats.distance(method='Equirect').magnitude)
