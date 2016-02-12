from typing import List
from urllib import request

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

from analysis.simplify import simplify, simplify_to_specific_length
from tests.assets import get_test_file_data


def make_image_url(trackpoints: List, best_fit):
    line = ','.join(["{0},{1}".format(x['lat'], x['lon'])
                     for x in trackpoints])

    polyline = ['color:0x000000',
                'width:5',
                line]

    params = ['key=nRieDryXmshAy6j3s7GZTTMmJHHNLw67',
              'type=map',
              'size=200,200',
              'polyline=' + '|'.join(polyline),
              'bestfit=' + ','.join([str(x) for x in best_fit]),
              'scalebar=false']

    return ("http://open.mapquestapi.com/staticmap/v4/getmap?" +
            '&'.join(params))


def make_image_for_track(trackpoints: List):
    """Generate a summary image for the given track"""

    # For now faking here.  In the future, create a test only endpoint
    # that returns the fake image, so this module doesn't need to know
    # anything about whether it is hitting a fake or not, and just get's
    # a URL to use.
    try:
        fake = settings.REMOTE_MAP_SOURCE != 'mapquest'
    except AttributeError:
        fake = True

    if fake:
        image = get_test_file_data('fake_map.png')
    else:
        lats = []
        lons = []
        for point in trackpoints:
            lats.append(point['lat'])
            lons.append(point['lon'])

        best_fit = [max(lats), max(lons), min(lats), min(lons)]

        url = make_image_url(simplify_to_specific_length(trackpoints),
                             best_fit)

        # TODO: Handle failed requests...
        remote_image = request.urlopen(url)
        image = remote_image.read()

    return ContentFile(image)
