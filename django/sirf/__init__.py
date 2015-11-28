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
from functools import reduce


class Parser(object):
    """SiRF parser for processing binary SiRF format"""

    def __init__(self):
        self.buffer = []
        self.state = 'init1'

        self.rxcksum = None
        self.cksummsb = None
        self.sizemsb = None
        self.dataleft = None

        self.fr_err = 0  # Framing error
        self.ck_err = 0  # Checksum error
        self.rx_cnt = 0  # Packet count

        self.pktq = []

    def __str__(self):
        return "Parsed SBN Data [{} Packets]".format(self.rx_cnt)

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
        pktcount = 0
        for data_frame in data:
            # print "Looking at 0x%02x, state = %s" % (data_frame, self.state)

            if self.state == 'init1':
                self.buffer = []
                if data_frame != 0xa0:
                    print("Start1 framing error, " +
                          "got 0x%02x, expected 0xa0" % data_frame)
                    self.fr_err += 1
                    continue

                self.state = 'init2'

            elif self.state == 'init2':
                if data_frame != 0xa2:
                    print("Start2 framing error, " +
                          "got 0x%02x, expected 0xa2" % data_frame)
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                self.state = 'sizemsb'

            elif self.state == 'sizemsb':
                # print "Size1 - 0x%02x" % (data_frame)
                if data_frame > 0x7f:
                    print("size msb too high (0x%02x)" % data_frame)
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                self.sizemsb = data_frame
                self.state = 'sizelsb'

            elif self.state == 'sizelsb':
                # print "Size2 - 0x%02x" % (data_frame)
                self.dataleft = self.sizemsb << 8 | data_frame

                if self.dataleft < 1:
                    print("size is too small (0x%04x)" % self.dataleft)
                    self.state = 'init1'
                    continue

                if self.dataleft > 1024:
                    print("size too large (0x%04x)" % self.dataleft)
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                # print "Pkt size - 0x%04x" % (self.dataleft)
                self.state = 'data'

            elif self.state == 'data':
                self.buffer.append(data_frame)
                self.dataleft -= 1

                if self.dataleft == 0:
                    self.state = 'cksum1'

            elif self.state == 'cksum1':
                self.cksummsb = data_frame
                self.state = 'cksum2'

            elif self.state == 'cksum2':
                self.rxcksum = self.cksummsb << 8 | data_frame
                self.state = 'end1'

            elif self.state == 'end1':
                if data_frame != 0xb0:
                    print("End1 framing error, got 0x%02x, expected 0xb0" %
                          data_frame)
                    self.state = 'init1'
                    self.fr_err += 1
                    continue

                self.state = 'end2'

            elif self.state == 'end2':
                if data_frame != 0xb3:
                    print("End2 framing error, got 0x%02x, expected 0xb3" %
                          data_frame)
                    self.fr_err += 1
                else:
                    pktsum = reduce(lambda x, y: x + y, self.buffer) & 0x7fff
                    if pktsum != self.rxcksum:
                        print("Checksum error: got 0x%04x, expected 0x%04x" %
                              (self.rxcksum, pktsum))
                        print("buffer is %s" % (str(self.buffer)))
                        self.state = 'init1'
                        self.ck_err += 1
                    else:
                        packet = self._decode_packet_in_buffer()
                        self.pktq.append(packet)
                        pktcount += 1
                        self.rx_cnt += 1

                self.state = 'init1'

            else:
                print("Invalid state %s! Resetting" % self.state)
                self.state = 'init1'

        return pktcount

    def _decode_packet_in_buffer(self):
        """Decode a packet in the buffer"""

        data = self.buffer
        if data[0] == 0x02:
            self._decode_0x02_packet(data)
        elif data[0] == 0x06:
            self._decode_0x06_packet(data)
        elif data[0] == 0x0a:
            self._decode_0x0a_packet(data)
        elif data[0] == 0x0b:
            self._decode_0x0b_packet(data)
        elif data[0] == 0x0c:
            self._decode_0x0c_packet(data)
        elif data[0] == 0x29:
            return self._decode_0x29_packet(data)
        elif data[0] == 0x34:
            self._decode_0x34_packet(data)
        elif data[0] == 0xa6:
            self._decode_0xa6_packet(data)
        else:
            print("Unknown packet type: {}".format(data[0]))

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
        datastr = ''.join([chr(x) for x in data[1:struct.calcsize(fmt)+1]])
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
