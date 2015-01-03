from datetime import datetime
from sirf import read_sbn

import pytz


class Stats(object):

    def __init__(self, sbn_file):
        self.sbn = read_sbn(sbn_file)
        self.timepoints = self.sbn.pktq
        self._filter_timepoints()

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

    def _filter_timepoints(self):
        self.timepoints = [x for x in self.timepoints if x is not None]

    def _convert_to_utc(self, time, date):
        return datetime.strptime('{} {}'.format(time, date),
                                 '%H:%M:%S %Y/%m/%d').replace(tzinfo=pytz.UTC)
                        
