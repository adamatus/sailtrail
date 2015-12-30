import shutil
import tempfile

from django.conf import settings


class TempMediaMixin(object):
    """Mixin to create MEDIA_ROOT in temp and tear down when complete."""

    @classmethod
    def setUpClass(cls):
        """Create temp directory and update MEDIA_ROOT and default storage."""
        print("I CGOT CALLED UP")
        super(TempMediaMixin, cls).setUpClass()
        settings._original_media_root = settings.MEDIA_ROOT
        settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
        cls._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = cls._temp_media
        print("SETTINGS MEDIA ROOT: {}".format(settings.MEDIA_ROOT))
        settings.DEFAULT_FILE_STORAGE = \
            'django.core.files.storage.FileSystemStorage'

    @classmethod
    def tearDownClass(cls):
        """Delete temp storage."""
        print("I GOT SHUT DOWN")
        super(TempMediaMixin, cls).tearDownClass()
        shutil.rmtree(cls._temp_media, ignore_errors=True)
        settings.MEDIA_ROOT = settings._original_media_root
        del settings._original_media_root
        settings.DEFAULT_FILE_STORAGE = settings._original_file_storage
        del settings._original_file_storage
