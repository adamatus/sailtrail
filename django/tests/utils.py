import shutil
import tempfile


class FileDeleter:
    """TestCase mixin to provide temporary space for files"""
    def setUp(self):
        """Create a new temporary directory"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove everything in the temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def my_round(num, places=3):
    """Round value to known number of places, for testing ease"""
    return int(num*10**places)/10**places
