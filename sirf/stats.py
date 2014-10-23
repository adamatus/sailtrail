from datetime import datetime
from sirf import read_sbn

import pytz

from pint import UnitRegistry

from math import sin, cos, sqrt, acos, atan2, radians


class Stats(object):

    def __init__(self, sbn_file):
        self.sbn = read_sbn(sbn_file)
        self.timepoints = self.sbn.pktq
        self._filter_timepoints()
        self.units = UnitRegistry()
        self.units.define('knots = knot')

    @property
    def full_start_time(self):
        return self._convert_to_utc(self.timepoints[0]['time'],
                                    self.timepoints[0]['date'])

    @property
    def full_end_time(self):
        return self._convert_to_utc(self.timepoints[-1]['time'],
                                    self.timepoints[-1]['date'])

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
    def tracks(self):
        return [{'lat': x['latitude'], 
                 'lon': x['longitude'],
                 'speed': x['sog'] * (self.units.m / self.units.s),
                 'time': x['time']}
                for x in self.timepoints]

    @property
    def speeds(self):
        return [x['sog'] * (self.units.m / self.units.s) 
                for x in self.timepoints]

    @property
    def max_speed(self):
        return max(self.speeds)

    def distance(self, method='EquirecApprox'):
        distance = 0
        for i in range(len(self.tracks)-1):
            distance += self._distance(self.tracks[i], 
                                       self.tracks[i+1], method)
        return distance * (self.units.m * 1000)

    def _filter_timepoints(self):
        self.timepoints = [x for x in self.timepoints 
                           if x is not None and x['satlst'] >= 3]

    def _convert_to_utc(self, time, date):
        return datetime.strptime('{} {}'.format(time, date),
                                 '%H:%M:%S %Y/%m/%d').replace(tzinfo=pytz.UTC)
                        
    def _distance(self, pos1, pos2, method='Haversine'):
        # Calculation formats from here 
        # http://www.movable-type.co.uk/scripts/latlong.html

        R = 6371.0  # Earth's radius in km
        lat1 = radians(pos1['lat'])
        lat2 = radians(pos2['lat'])
        lon1 = radians(pos1['lon'])
        lon2 = radians(pos2['lon'])

        # Haversine
        if method == 'Haversine':
            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        elif method == 'SphLawCos':
            dlon = lon2 - lon1

            return acos(sin(lat1)*sin(lat2) + 
                        cos(lat1)*cos(lat2)*cos(dlon)) * R

        else:  # method == Equirectangular approx
            x = (lon2-lon1) * cos((lat1+lat2)/2)
            y = (lat2-lat1)
            return sqrt(x**2 + y**2) * R

