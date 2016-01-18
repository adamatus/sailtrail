import os

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
