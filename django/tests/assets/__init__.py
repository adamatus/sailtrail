"""Helper to provide test data"""
import os

ASSET_PATH = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'bad.txt': 'bad.txt',
    'kite-session1.sbn': 'kite-session1.sbn',
    'kite-session2.sbn': 'kite-session2.sbn',
    'test.sbn': 'test.sbn',
    'test-small.sbn': 'test-small.sbn',
    'tiny.SBN': 'tiny.SBN',
    'tiny-run.gpx': 'tiny-run.gpx',
    'tiny-run-2.gpx': 'tiny-run-2.gpx',
    'map.png': 'map.png',
    'fake_map.png': 'fake_map.png',
}


def get_test_file_data(filename):
    """Read the data for a specific file"""
    file = FILES[filename]
    with open(os.path.join(ASSET_PATH, file), 'rb') as f:
        return f.read()


def get_test_file_path(filename):
    """Get the full absolute filepath of the file"""
    file = FILES[filename]
    return os.path.join(ASSET_PATH, file)
