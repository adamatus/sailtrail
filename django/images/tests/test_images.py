from unittest.mock import patch, sentinel, MagicMock
from urllib.error import HTTPError

from django.core.files.base import ContentFile

from images import make_image_for_track, make_image_url, compute_best_fit, \
    get_image_from_url


class TestImages:

    def test_make_image_url_returns_correct_url(self):
        # Given a trackpoint and best fit array
        pos = [{"lat": 1, "lon": 1}, {"lat": 2, "lon": 2}]
        best_fit = [40, -100, 42, -102]

        # When making the image url
        url = make_image_url(pos, best_fit)

        assert url.startswith(
            "http://open.mapquestapi.com/staticmap/v4/getmap?")
        assert "?key=" in url
        assert "&type=map&" in url
        assert "&size=200,200&" in url
        assert "&polyline=color:0x000000|width:5|1,1,2,2&" in url
        assert "&bestfit=40,-100,42,-102&" in url
        assert "&scalebar=false" in url

    def test_compute_best_fit(self):
        pos = [{"lat": 1, "lon": 11}, {"lat": 2, "lon": 22}]
        assert compute_best_fit(pos) == [2, 22, 1, 11]

        pos = [{"lat": 2, "lon": 22},
               {"lat": 3, "lon": 33},
               {"lat": -1, "lon": -11}]
        assert compute_best_fit(pos) == [3, 33, -1, -11]

    @patch('images.request')
    def test_get_image_for_url_returns_none_if_not_200(self, request_mock):
        response = MagicMock(status=201)
        request_mock.urlopen.return_value.__enter__.return_value = response

        image = get_image_from_url(sentinel.url)

        assert image is None

        request_mock.urlopen.assert_called_once_with(sentinel.url)

    @patch('images.request')
    def test_get_image_for_url_returns_none_if_request_throws(self,
                                                              request_mock):
        request_mock.urlopen.side_effect = HTTPError(sentinel.url, 400, "bad",
                                                     [], [])

        image = get_image_from_url(sentinel.url)

        assert image is None

        request_mock.urlopen.assert_called_once_with(sentinel.url)

    @patch('images.request')
    def test_get_image_for_url_returns_image_data(self,
                                                  request_mock):
        response = MagicMock()
        response.status = 200
        response.read.return_value = sentinel.data

        request_mock.urlopen.return_value.__enter__.return_value = response

        image = get_image_from_url(sentinel.url)

        assert image == sentinel.data

        request_mock.urlopen.assert_called_once_with(sentinel.url)

    @patch('images.uuid')
    @patch('images.get_image_from_url')
    @patch('images.make_image_url')
    @patch('images.simplify_to_specific_length')
    @patch('images.compute_best_fit')
    def test_make_image_for_track_returns_content_file(self,
                                                       best_fit_mock,
                                                       simplify_mock,
                                                       make_url_mock,
                                                       get_image_mock,
                                                       uuid_mock):
        best_fit_mock.return_value = sentinel.best_fit
        simplify_mock.return_value = sentinel.points
        make_url_mock.return_value = sentinel.url
        get_image_mock.return_value = b"XXXX"
        uuid_mock.uuid4.return_value = "1234"

        # When making an image for track
        image = make_image_for_track(sentinel.trackpoints)

        # Then an image is returned
        assert isinstance(image, ContentFile)
        assert image.name == "1234.png"
        assert image.read() == b"XXXX"

        best_fit_mock.assert_called_once_with(sentinel.trackpoints)
        simplify_mock.assert_called_once_with(sentinel.trackpoints)
        make_url_mock.assert_called_once_with(sentinel.points,
                                              sentinel.best_fit)
        get_image_mock.assert_called_once_with(sentinel.url)

    @patch('images.uuid')
    @patch('images.get_test_file_data')
    @patch('images.settings')
    def test_make_image_for_track_returns_content_file_for_fake(
        self,
        settings_mock,
        get_data_mock,
        uuid_mock
    ):

        settings_mock.REMOTE_MAP_SOURCE = 'other'
        get_data_mock.return_value = b'YYYY'
        uuid_mock.uuid4.return_value = "1234"

        # When making an image for track
        image = make_image_for_track(sentinel.trackpoints)

        # Then an image is returned
        assert isinstance(image, ContentFile)
        assert image.name == "1234.png"
        assert image.read() == b"YYYY"
