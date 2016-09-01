import uuid
from typing import List
from urllib import request
from urllib.error import HTTPError

from django.conf import settings
from django.core.files.base import ContentFile

from analysis.simplify import simplify_to_specific_length
from tests.assets import get_test_file_data


def make_image_url(trackpoints: List, best_fit):
    line = ','.join(["{0},{1}".format(x['lat'], x['lon'])
                     for x in trackpoints])

    polyline = ['color:0x000000',
                'width:5',
                line]

    params = ['key=nRieDryXmshAy6j3s7GZTTMmJHHNLw67',
              'type=map',
              'size=400,400',
              'polyline=' + '|'.join(polyline),
              'bestfit=' + ','.join([str(x) for x in best_fit]),
              'scalebar=false']

    return ("http://open.mapquestapi.com/staticmap/v4/getmap?" +
            '&'.join(params))


def compute_best_fit(trackpoints):
    """Compute the best fit rectangle for the track

    TODO: I really shouldn't be passing around a list of dicts, I should
    have a proper object, which has methods for this.  See gpxpy objects"""
    max_lat = trackpoints[0]['lat']
    min_lat = trackpoints[0]['lat']
    max_lon = trackpoints[0]['lon']
    min_lon = trackpoints[0]['lon']

    for point in trackpoints:
        if point['lat'] > max_lat:
            max_lat = point['lat']
        if point['lat'] < min_lat:
            min_lat = point['lat']
        if point['lon'] > max_lon:
            max_lon = point['lon']
        if point['lon'] < min_lon:
            min_lon = point['lon']

    return [max_lat, max_lon, min_lat, min_lon]


def get_image_from_url(url):
    """Get raw image data from a url"""
    try:
        with request.urlopen(url) as remote_image:
            if remote_image.status != 200:
                # For now just return None if request failed
                return None
            return remote_image.read()
    except HTTPError:
        return None


def make_image_for_track(trackpoints: List) -> ContentFile:
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
        best_fit = compute_best_fit(trackpoints)
        points = simplify_to_specific_length(trackpoints)

        url = make_image_url(points, best_fit)
        image = get_image_from_url(url)

    return ContentFile(image, name="{}.png".format(uuid.uuid4()))
