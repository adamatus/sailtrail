from django.core.files.images import ImageFile

from images import make_image_for_track


class TestImages:

    def test_make_image_for_track_returns_image(self):
        # Given some trackpoints
        pos = [{"lat": 1, "lon": 1}, {"lat": 2, "lon": 2}]

        # When making an image for track
        image = make_image_for_track(pos)

        # Then an image is returned
        assert isinstance(image, ImageFile)
