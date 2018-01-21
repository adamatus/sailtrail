"""
SiRF Parser
Based on Python SiRF parser by Daniel O'Connor (See license below)
(http://www.dons.net.au/~darius/hgwebdir.cgi/sirf)

Changes made:
 - Updated for Python3
 - Stripped out all code for reading/writing to active device
 - Switched from reduce(lambda x+y) to ''.join for char concat
 - Minor tweaks to names/order
 - Added function to directly read SBN file

Copyright (c) 2009
     Daniel O'Connor <darius@dons.net.au>.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

import struct
from datetime import datetime
from functools import reduce

import pytz
from django.core.files.uploadedfile import InMemoryUploadedFile


class Parser(object):
    """SiRF parser for processing binary SiRF format"""

    def __init__(self):

        keys = ['fr', 'ck', 'rx']
        self.counts = dict(zip(keys, [0, 0, 0]))

        self.buffer = []
        self.state = 'init1'
        self.dataleft = 0

        self.pktq = []

    def __str__(self):
        return "Parsed SBN Data [{} Packets]".format(self.counts['rx'])

    def processstr(self, data):
        """Process a string of data

        Parameters
        ----------
        data
            The data stream to process

        Returns
        -------
        The number of packets processed
        """
        return self.process([ord(x) for x in data])

    def process(self, data):
        """Process a list of data

        Parameters
        ----------
        data : list
            The data stream to process

        Returns
        -------
        int
            The number of packets processed
        """
        for data_frame in data:
            try:
                if self.state == 'init1':
                    self.process_init1_frame(data_frame)
                elif self.state == 'init2':
                    self.process_init2_frame(data_frame)
                elif self.state == 'sizemsb':
                    sizemsb = self.process_size_msb(data_frame)
                elif self.state == 'sizelsb':
                    self.process_size_lsb(data_frame, sizemsb)
                elif self.state == 'data':
                    self.process_data(data_frame)
                elif self.state == 'cksum1':
                    cksummsb = self.process_checksum1(data_frame)
                elif self.state == 'cksum2':
                    rxcksum = self.process_checksum2(data_frame, cksummsb)
                elif self.state == 'end1':
                    self.process_end1(data_frame)
                elif self.state == 'end2':
                    self.process_end2(data_frame, rxcksum)
            except ChecksumErrorException:
                self.counts['ck'] += 1
                self.state = 'init1'
            except FrameErrorException:
                self.counts['fr'] += 1
                self.state = 'init1'

        return self.counts['rx']

    def process_init1_frame(self, data_frame):
        """Process the init1 frame

        Parameters
        ----------
        data_frame : int
        """
        self.buffer = []
        if data_frame == 0xa0:
            self.state = 'init2'
        else:
            raise FrameErrorException('init1', 0xa0, data_frame)

    def process_init2_frame(self, data_frame):
        """Process the init2 frame

        Parameters
        ----------
        data_frame : int
        """
        if data_frame == 0xa2:
            self.state = 'sizemsb'
        else:
            raise FrameErrorException('init2', 0xa2, data_frame)

    def process_size_msb(self, data_frame):
        """Process the most significant byte of the size frame

        Parameters
        ----------
        data_frame : int
        """
        if data_frame <= 0x7f:
            self.state = 'sizelsb'
            return data_frame
        else:
            raise FrameErrorException('sizemsb', None, data_frame)

    def process_size_lsb(self, data_frame, sizemsb):
        """Process the least significant byte of the size frame

        Parameters
        ----------
        sizemsb : int
        data_frame : int
        """
        dataleft = sizemsb << 8 | data_frame
        if 1 < dataleft <= 1024:
            self.state = 'data'
            self.dataleft = dataleft
        else:
            raise FrameErrorException('sizelsb', None, dataleft)

    def process_data(self, data_frame):
        """Process a data frame

        Parameters
        ----------
        data_frame : int
        """
        self.buffer.append(data_frame)
        self.dataleft -= 1
        if self.dataleft == 0:
            self.state = 'cksum1'

    def process_checksum1(self, data_frame):
        """Process most significant bit of checksum frame

        Parameters
        ----------
        data_frame : int
        """
        cksummsb = data_frame
        self.state = 'cksum2'
        return cksummsb

    def process_checksum2(self, data_frame, checksum_msb):
        """Process least significant bit of checksum frame

        Parameters
        ----------
        data_frame : int
        checksum_msb : int
        """
        rxcksum = checksum_msb << 8 | data_frame
        self.state = 'end1'
        return rxcksum

    def process_end1(self, data_frame):
        """Process a data frame

        Parameters
        ----------
        data_frame : int
        """
        if data_frame == 0xb0:
            self.state = 'end2'
        else:
            raise FrameErrorException('end1', 0xb0, data_frame)

    def process_end2(self, data_frame, rxcksum):
        """Process a data frame

        Parameters
        ----------
        data_frame : int
        rxcksum : int
        """
        if data_frame == 0xb3:
            pktsum = reduce(lambda x, y: x + y, self.buffer) & 0x7fff
            self.state = 'init1'
            if pktsum == rxcksum:
                packet = self._decode_packets_in_buffer(self.buffer)
                self.pktq.append(packet)
                self.counts['rx'] += 1
            else:
                raise ChecksumErrorException('end2', pktsum, rxcksum)
        else:
            raise FrameErrorException('end2', 0xb3, data_frame)

    def _decode_packets_in_buffer(self, data):
        """Decode packets in the buffer"""

        header = data[0]

        if header == 0x02:
            self._decode_0x02_packet(data)
        elif header == 0x06:
            self._decode_0x06_packet(data)
        elif header == 0x0a:
            self._decode_0x0a_packet(data)
        elif header == 0x0b:
            self._decode_0x0b_packet(data)
        elif header == 0x0c:
            self._decode_0x0c_packet(data)
        elif header == 0x29:
            return self._decode_0x29_packet(data)
        elif header == 0x34:
            self._decode_0x34_packet(data)
        elif header == 0xa6:
            self._decode_0xa6_packet(data)
        else:
            print("Unknown packet type: {}".format(data[0]))

        return None

    @staticmethod
    def _decode_0xa6_packet(data):
        """Decode a 0xa6 packet"""
        print("Message rate : MID 0x%02x, rate 0x%02x" %
              (data[2], data[3]))

    @staticmethod
    def _decode_0x34_packet(data):
        """Decode a 0x34 Packet"""
        fmt = '>BBBBBHHIB'
        datastr = ''.join([chr(x) for x in data[1:struct.calcsize(fmt) + 1]])
        (hour, minute, second, day, month, year, offsetint, offsetfrac,
         status) = struct.unpack(fmt, bytes(datastr, 'Latin-1'))
        offset = offsetint + float(offsetfrac) / 1e9
        print(("PPS : %04d/%02d/%02d %02d:%02d:%02d, " +
               "Offset : %.9f, Status : 0x%02x") %
              (year, month, day, hour, minute, second, offset, status))

    @staticmethod
    def _decode_0x29_packet(data):
        """Decode a 0x29 Packet"""
        fixtype = {
            0: "none",
            1: "1-SV KF",
            2: "2-SV KF",
            3: "3-SV KF",
            4: "4+-SV KF",
            5: "2D",
            6: "3D",
            7: "DR"
        }
        fmt = '>HHHIHBBBBHIiiiiBHHHHHIIIHIIIIIHHBBB'
        datastr = ''.join([chr(x) for x in data[1:struct.calcsize(fmt) + 1]])
        keys = ['navval', 'navtype', 'ewn', 'tow', 'year', 'month', 'day',
                'hour', 'minute', 'second', 'satlst', 'latitude', 'longitude',
                'alt_elip', 'alt_msl', 'datum', 'sog', 'cog', 'magvar',
                'climbrate', 'headrate', 'est_horiz_pos_err',
                'est_vert_pos_err', 'est_time_err', 'est_horiz_vel_err',
                'clock_bias', 'clock_bias_err', 'clock_drift',
                'clock_drift_err', 'distance', 'dist_err', 'heading_err',
                'numsvs', 'hdop', 'addmodeinfo']
        parsed = dict(zip(keys,
                          struct.unpack(fmt, bytes(datastr, 'Latin-1'))))

        return {
            # GPS time of week (sec)
            'tow': float(parsed['tow']) / 1e3,
            # Seconds
            'second': float(parsed['second']) / 1e3,
            # Latitude/Longitude (degrees)
            'latitude': float(parsed['latitude']) / 1e7,
            'longitude': float(parsed['longitude']) / 1e7,
            # Altitude from ellipsoid (meters)
            'alt_elip': float(parsed['alt_elip']) / 1e2,
            # Altitude from mean sea level (meters)
            'alt_msl': float(parsed['alt_msl']) / 1e2,
            # Speed over ground ("m/s")
            'sog': float(parsed['sog']) / 1e2,
            # Course over ground ("degrees clockwise from true north")
            'cog': float(parsed['cog']) / 1e2,
            # Climb rate ("m/s")
            'climbrate': float(parsed['climbrate']) / 1e2,
            # Heading rate ("deg/s")
            'headrate': float(parsed['headrate']) / 1e2,
            # Estimated horizonal position error (meters)
            'estHPE': float(parsed['est_horiz_pos_err']) / 1e2,
            # Estimated vertical position error (meters)
            'estVPE': float(parsed['est_vert_pos_err']) / 1e2,
            # Estimated time error (seconds)
            'estTE': float(parsed['est_time_err']) / 1e2,
            # Estimated horizontal velocity error (m/s)
            'estHVE': float(parsed['est_horiz_vel_err']) / 1e2,
            # Clock bias ("m")
            'clockbias': float(parsed['clock_bias']) / 1e2,
            # Clock bias error ("meters")
            'CBerr': float(parsed['clock_bias_err']) / 1e2,
            # Clock drift ("m/s")
            'clockdrift': float(parsed['clock_drift']) / 1e2,
            # Clock drift error ("m/s")
            'CDerr': float(parsed['clock_drift_err']) / 1e2,
            # Distance travelled since reset (meters)
            'distance': parsed['distance'],
            # Distance Error (meters)
            'distanceErr': parsed['dist_err'],
            # Heading error (degrees)
            'headErr': float(parsed['heading_err']) / 1e2,
            # Number of sats
            'numsvs': parsed['numsvs'],
            # Horizontal dilution of precision (.2 resolution)
            'hdop': float(parsed['hdop']) / 5,
            # Fix type
            'fixtype': fixtype[parsed['navtype'] & 0x7],
            # Bitmap of sats used in solution Bit 0 = Sat 1, etc.
            'satlst': parsed['satlst'],
            # Map datum to which lat, long, alt apply: 21 = WGS-84
            'datum': parsed['datum'],
            # Magnetic variation [NOT IMPLEMENTED]
            'magvar': parsed['magvar'],
            'date': '{:02}/{:02}/{:02}'.format(parsed['year'],
                                               parsed['month'],
                                               parsed['day']),
            'time': '{:02}:{:02}:{:02}'.format(parsed['hour'],
                                               parsed['minute'],
                                               int(parsed['second'] / 1e3))
        }

    @staticmethod
    def _decode_0x0c_packet(data):
        """Decode a 0x0c Packet"""
        print("                          Cmd NAck : 0x%02x" % (data[1]))

    @staticmethod
    def _decode_0x0b_packet(data):
        """Decode a 0x0b Packet"""
        print("                          Cmd Ack  : 0x%02x" % (data[1]))

    @staticmethod
    def _decode_0x0a_packet(data):
        """Decode a 0x0a Packet"""
        errid = data[1] << 8 | data[2]
        dlen = (data[3] << 8 | data[4]) * 4
        print("                          Error ID : 0x%04x" % errid)
        if dlen > 0:
            print("                          Length   : 0x%04x" % dlen)
            print("                          Payload  : %s" % (data[5:]))

    @staticmethod
    def _decode_0x06_packet(data):
        """Decode a 0x06 Packet"""
        nulidx = data.index(0)
        print("SW Ver : %s" % ''.join([chr(x) for x in data[1:nulidx]]))

    @staticmethod
    def _decode_0x02_packet(data):
        """Decode a 0x02 Packet"""
        fmt = '>iiihhhBBBhIB'
        keys = ['xpos', 'ypos', 'zpos', 'xvel', 'yvel', 'zvel', 'mode1',
                'hdop', 'mode2', 'gpsweek', 'gpstow', 'nsats']
        datastr = ''.join([chr(x) for x in data[1:struct.calcsize(fmt) + 1]])
        parsed = dict(zip(keys,
                          struct.unpack(fmt, bytes(datastr, 'Latin-1'))))

        satprn = []
        for i in range(parsed['nsats']):
            satprn.append(data[struct.calcsize(fmt) - 1 + i])

        print("Position: X: " +
              "%d m, Y: %d m, Z: %d m" % (parsed['xpos'], parsed['ypos'],
                                          parsed['zpos']))
        print("Velocity: X: %.2f m/s, Y: %.2f m/s, Z: %.2f m/s" %
              (float(parsed['xvel']) / 8,
               float(parsed['yvel']) / 8,
               float(parsed['zvel']) / 8))
        print("HDOP: " +
              "%.1f, Week: %d, TOW: %.2f seconds" %
              (float(parsed['hdop']) / 5,
               parsed['gpsweek'],
               float(parsed['gpstow']) / 100))


def read_sbn(filename):
    """Read a .SBN binary file and process it

    Parameters
    ----------
    filename : string
        Path to SBN file

    Returns
    -------
    Parser
        Pre-parsed Parser

    """
    with open(filename, 'rb') as file:
        sbn = file.read()
    parser = Parser()
    parser.process(sbn)
    return parser


class FrameErrorException(Exception):
    """Frame error"""
    def __init__(self, cur_state, expected, actual):
        super(FrameErrorException, self).__init__()
        self.cur_state = cur_state
        self.expected = expected
        self.actual = actual


class ChecksumErrorException(FrameErrorException):
    """Data checksum error"""
    pass


def create_trackpoints(track,
                       uploaded_file: InMemoryUploadedFile,
                       model):
    """Create list of ActivityTrackpoints for SBN file"""
    data = Parser()
    data.process(uploaded_file.read())
    # filter out Nones
    data = [x for x in data.pktq
            if x is not None and x['fixtype'] != 'none']

    insert = []
    app = insert.append  # cache append method for speed.. maybe?
    fmt = '%H:%M:%S %Y/%m/%d'
    for track_point in data:
        app(model(
            lat=track_point['latitude'],
            lon=track_point['longitude'],
            sog=track_point['sog'],
            timepoint=datetime.strptime('{} {}'.format(track_point['time'],
                                                       track_point['date']),
                                        fmt).replace(tzinfo=pytz.UTC),
            track=track))
    return insert
