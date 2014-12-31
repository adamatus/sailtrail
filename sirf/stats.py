import numpy as np

from pint import UnitRegistry


class Stats(object):

    def __init__(self, trackpoints):
        self.trackpoints = trackpoints
        self.units = UnitRegistry()
        self.units.define('knots = knot')

    @property
    def full_start_time(self):
        return self.trackpoints[0]['timepoint']

    @property
    def full_end_time(self):
        return self.trackpoints[-1]['timepoint']

    @property
    def start_time(self):
        return self.full_start_time.time()

    @property
    def start_date(self):
        return self.full_start_time.date()

    @property
    def end_time(self):
        return self.full_end_time.time()

    @property
    def duration(self):
        return self.full_end_time - self.full_start_time

    @property
    def speeds(self):
        return [x['sog'] * (self.units.m / self.units.s)
                for x in self.trackpoints]

    @property
    def max_speed(self):
        return max(self.speeds)

    def distance(self, method='EquirecApprox'):
        R = 6371.0  # Earth's radius in km

        lats = np.radians(np.asarray([x['lat'] for x in self.trackpoints]))
        lons = np.radians(np.asarray([x['lon'] for x in self.trackpoints]))

        lat1 = lats[0:-1]
        lat2 = lats[1:]
        lon1 = lons[0:-1]
        lon2 = lons[1:]

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        if method == 'Haversine':
            a = ((np.sin(dlat/2))**2 +
                 np.cos(lat1) * np.cos(lat2) * (np.sin(dlon/2))**2)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            dist = R * c

        elif method == 'SphLawCos':
            dist = np.arccos(np.sin(lat1)*np.sin(lat2) +
                             np.cos(lat1)*np.cos(lat2)*np.cos(dlon)) * R
        else:
            x = (lon2-lon1) * np.cos((lat1+lat2)/2)
            y = (lat2-lat1)
            dist = np.sqrt(x**2 + y**2) * R

        return np.sum(dist) * (self.units.m * 1000)
