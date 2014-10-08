import unittest
import os
import sirf

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_assets')
TEST_FILE = os.path.join(ASSET_DIR, 'test.sbn')


class SiRFTest(unittest.TestCase):
    """Tests for SiRF Processing"""

    def test_reading_of_sirf_file(self):
        p = sirf.read_sbn(TEST_FILE)        
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

