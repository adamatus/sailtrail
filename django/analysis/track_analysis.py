"""Track analysis module"""
from typing import Iterable

import numpy as np

from activities import UNIT_SETTING, UNITS, DATETIME_FORMAT_STR
from sirf.stats import Stats


def make_json_from_trackpoints(pos: Iterable) -> dict:
    """Helper method to return JSON data for trackpoints

    This method takes the list of trackpoints, computes stats for it,
    then returns the results as an object with a list for each field,
    rather than as a list of objects.  This was found to be significantly
    smaller over-the-wire."""

    stats = Stats(pos)
    # distances = stats.distances()
    # distances = np.round(np.append(distances, distances[-1]), 3)

    bearings = stats.bearing()
    # hack to get same size arrays (just repeat final element)
    bearings = np.round(np.append(bearings, bearings[-1]))

    speed = []
    time = []
    lat = []
    lon = []

    for position in pos:
        lat.append(position['lat'])
        lon.append(position['lon'])
        speed.append(round(
            (position['sog'] * UNITS.m / UNITS.s).to(
                UNIT_SETTING['speed']).magnitude,
            2))
        time.append(position['timepoint'].strftime(DATETIME_FORMAT_STR))

    return dict(bearing=bearings.tolist(), time=time,
                speed=speed, lat=lat, lon=lon)
