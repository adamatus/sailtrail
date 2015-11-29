"""
Helper module to compute stats on GPS tracks
"""

import numpy as np

from pint import UnitRegistry


class Stats(object):
    """ Stats object to compute common statistics for a GPS track"""

    def __init__(self, trackpoints):
        self.trackpoints = trackpoints
        self.units = UnitRegistry()
        self.units.define('knots = knot')

    @property
    def full_start_time(self):
        """Get the start date and time of the track"""
        return self.trackpoints[0]['timepoint']

    @property
    def full_end_time(self):
        """Get the end date and time of the track"""
        return self.trackpoints[-1]['timepoint']

    @property
    def start_time(self):
        """Get the start time of the track"""
        return self.full_start_time.time()

    @property
    def start_date(self):
        """Get the start date of the track"""
        return self.full_start_time.date()

    @property
    def end_time(self):
        """Get the end time of the track"""
        return self.full_end_time.time()

    @property
    def duration(self):
        """Get the duration of the track"""
        return self.full_end_time - self.full_start_time

    @property
    def speeds(self):
        """Get the speed over ground at each trackpoint"""
        return [x['sog'] * (self.units.m / self.units.s)
                for x in self.trackpoints]

    @property
    def max_speed(self):
        """Get the max instantaneous speed during the track"""
        return max(self.speeds)

    def distances(self, method='EquirecApprox'):
        """Get the trackpoint to trackpoint distances across the track

        Parameters
        ----------
        method : string
            The approximation methods to use for computing distances.

            'EquirecApprox' (default) uses a rectangular approximation,
            ignoring that the surface of the earth is round.  Fast, but not
            as accurate, especially for longer distances between points.

            'Haversine' is more accurate, but slower.

            'SphLawCos' is more accurate, but slower.
        """
        earths_radius = 6371.0  # in km

        lats = np.radians(np.asarray([x['lat'] for x in self.trackpoints]))
        lons = np.radians(np.asarray([x['lon'] for x in self.trackpoints]))

        lat1 = lats[0:-1]
        lat2 = lats[1:]
        lon1 = lons[0:-1]
        lon2 = lons[1:]

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        if method == 'Haversine':
            a_val = ((np.sin(dlat / 2))**2 +
                     np.cos(lat1) * np.cos(lat2) * (np.sin(dlon/2))**2)
            dist = earths_radius * 2 * np.arctan2(np.sqrt(a_val),
                                                  np.sqrt(1 - a_val))

        elif method == 'SphLawCos':
            dist = (np.arccos((np.sin(lat1) * np.sin(lat2)) +
                              (np.cos(lat1) * np.cos(lat2) * np.cos(dlon))) *
                    earths_radius)
        else:
            x_vals = (lon2-lon1) * np.cos((lat1+lat2)/2)
            y_vals = (lat2-lat1)
            dist = np.sqrt(x_vals**2 + y_vals**2) * earths_radius

        return dist * (self.units.m * 1000)

    def distance(self, method='EquirecApprox'):
        """Get the total distance covered by the track

        Parameters
        ----------
        method : string
            The approximation methods to use for computing distances. See
            `distances()` for details on the available methods.
        """
        dist = self.distances(method)
        return np.sum(dist)

    def bearing(self):
        """Calculate the instantaneous bearing at each trackpoint"""

        lats = np.deg2rad(np.asarray([x['lat'] for x in self.trackpoints]))
        lons = np.deg2rad(np.asarray([x['lon'] for x in self.trackpoints]))

        lat1 = lats[0:-1]
        lat2 = lats[1:]
        dlon = lons[1:] - lons[0:-1]

        x_vals = (np.cos(lat1) * np.sin(lat2)) \
            - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))
        y_vals = np.sin(dlon) * np.cos(lat2)
        brn = np.rad2deg(np.arctan2(y_vals, x_vals))
        return np.mod(brn+360, 360)
