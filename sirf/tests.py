import unittest
import os
import sirf
from sirf.stats import Stats

from datetime import date, time, timedelta

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_assets')
TEST_FILE = os.path.join(ASSET_DIR, 'test-small.sbn')


class SiRFTest(unittest.TestCase):
    """Tests for SiRF Processing"""

    def test_reading_of_sirf_file(self):
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
        self.stats = Stats(TEST_FILE)

    def test_get_start_time(self):
        self.assertEquals(time(2, 45, 13), self.stats.start_time)

    def test_get_end_time(self):
        self.assertEquals(time(2, 45, 40), self.stats.end_time)

    def test_get_start_date(self):
        self.assertEquals(date(2014, 9, 28), self.stats.start_date)

    def test_get_duration(self):
        self.assertEquals(timedelta(0, 27), self.stats.duration)

    def test_get_tracks(self):
        tracks = self.stats.tracks
        self.assertEquals(28, len(tracks))
        self.assertAlmostEquals(-122.6243636, tracks[0]['lon'])
        self.assertAlmostEquals(45.604354, tracks[0]['lat'])

    def test_get_speeds(self):
        speeds = self.stats.speeds
        self.assertEquals(28, len(speeds))
        self.assertAlmostEquals(2.19, speeds[0].magnitude)

    def test_get_max_speed(self):
        self.assertEqual('2.53 m / s', '{:~}'.format(self.stats.max_speed))

    def test_get_distance(self):
        self.assertAlmostEquals(
            59.12590197, self.stats.distance(method='Haversine').magnitude)
        self.assertAlmostEquals(
            59.11451088, self.stats.distance(method='SphLawCos').magnitude)
        self.assertAlmostEquals(
            59.12590197, self.stats.distance(method='Equirect').magnitude)
