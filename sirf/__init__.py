# Based on Python SiRF parser by Daniel O'Connor (See license below)
# (http://www.dons.net.au/~darius/hgwebdir.cgi/sirf)
# 
# Changes made:
#  - Updated for Python3
#  - Stripped out all code for reading/writing to active device
#  - Switched from reduce(lambda x+y) to ''.join for char concat
#  - Minor tweaks to names/order
#  - Added function to directly read SBN file

# Copyright (c) 2009
#      Daniel O'Connor <darius@dons.net.au>.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import struct
from functools import reduce


class Parser(object):

    def __init__(self, s=None):
        self.buffer = []
        self.state = 'init1'

        self.fr_err = 0  # Framing error
        self.ck_err = 0  # Checksum error
        self.rx_cnt = 0  # Packet count

        self.pktq = []
        self.s = s

    def __str__(self):
        return "Parsed SBN Data [{} Packets]".format(self.rx_cnt)

    def processstr(self, data):
        return self.process(list(map(ord, data)))

    def process(self, data):
        pktcount = 0
        for d in data:
            # print "Looking at 0x%02x, state = %s" % (d, self.state)

            if (self.state == 'init1'):
                self.buffer = []
                if (d != 0xa0):
                    print("Start1 framing error, " +
                          "got 0x%02x, expected 0xa0" % d)
                    self.fr_err += 1
                    continue

                self.state = 'init2'

            elif (self.state == 'init2'):
                if (d != 0xa2):
                    print("Start2 framing error, " +
                          "got 0x%02x, expected 0xa2" % d)
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                self.state = 'sizemsb'

            elif (self.state == 'sizemsb'):
                # print "Size1 - 0x%02x" % (d)
                if d > 0x7f:
                    print("size msb too high (0x%02x)" % (d))
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                self.sizemsb = d
                self.state = 'sizelsb'

            elif (self.state == 'sizelsb'):
                # print "Size2 - 0x%02x" % (d)
                self.dataleft = self.sizemsb << 8 | d

                if self.dataleft < 1:
                    print("size is too small (0x%04x)" % (self.dataleft))
                    self.state = 'init1'
                    continue

                if self.dataleft > 1024:
                    print("size too large (0x%04x)" % (self.dataleft))
                    self.fr_err += 1
                    self.state = 'init1'
                    continue

                # print "Pkt size - 0x%04x" % (self.dataleft)
                self.state = 'data'

            elif (self.state == 'data'):
                self.buffer.append(d)
                self.dataleft = self.dataleft - 1

                if self.dataleft == 0:
                    self.state = 'cksum1'

            elif (self.state == 'cksum1'):
                self.cksummsb = d
                self.state = 'cksum2'

            elif (self.state == 'cksum2'):
                self.rxcksum = self.cksummsb << 8 | d
                self.state = 'end1'

            elif (self.state == 'end1'):
                if (d != 0xb0):
                    print("End1 framing error, got 0x%02x, expected 0xb0" % d)
                    self.state = 'init1'
                    self.fr_err += 1
                    continue

                self.state = 'end2'

            elif (self.state == 'end2'):
                if (d != 0xb3):
                    print("End2 framing error, got 0x%02x, expected 0xb3" % d)
                    self.fr_err += 1
                else:
                    pktsum = reduce(lambda x, y: x + y, self.buffer) & 0x7fff
                    if (pktsum != self.rxcksum):
                        print("Checksum error: got 0x%04x, expected 0x%04x" %
                              (self.rxcksum, pktsum))
                        print("buffer is %s" % (str(self.buffer)))
                        self.state = 'init1'
                        self.ck_err += 1
                    else:
                        p = self._decode_packet_in_buffer()
                        self.pktq.append(p)
                        pktcount += 1
                        self.rx_cnt += 1

                self.state = 'init1'

            else:
                print("Invalid state %s! Resetting" % (self.state))
                self.state = 'init1'

        return pktcount

    def _decode_packet_in_buffer(self):

        data = self.buffer
        if data[0] == 0x02:
            fmt = '>iiihhhBBBhIB'
            datastr = ''.join(list(map(chr, data[1:struct.calcsize(fmt) + 1])))

            (xpos, ypos, zpos, xvel, yvel, zvel, mode1, hdop,
             mode2, gpsweek, gpstow, nsats
             ) = struct.unpack(fmt, bytes(datastr, 'Latin-1'))

            satprn = []
            for i in range(nsats):
                satprn.append(data[struct.calcsize(fmt) - 1 + i])

            xvel = float(xvel) / 8
            yvel = float(yvel) / 8
            zvel = float(zvel) / 8
            hdop = float(hdop) / 5
            gpstow = float(gpstow) / 100

            print("Position: X: " +
                  "%d m, Y: %d m, Z: %d m" % (xpos, ypos, zpos))
            print("Velocity: X: " +
                  "%.2f m/s, Y: %.2f m/s, Z: %.2f m/s" % (xvel, yvel, zvel))
            print("HDOP: " +
                  "%.1f, Week: %d, TOW: %.2f seconds" %
                  (hdop, gpsweek, gpstow))

        elif data[0] == 0x06:
            nulidx = data.index(0)
            print("SW Ver : %s" % ''.join(list(map(chr, data[1:nulidx]))))

        elif data[0] == 0x0a:
            errid = data[1] << 8 | data[2]
            dlen = (data[3] << 8 | data[4]) * 4
            print("                          Error ID : 0x%04x" % (errid))
            if dlen > 0:
                print("                          Length   : 0x%04x" % (dlen))
                print("                          Payload  : %s" % (data[5:]))

        elif data[0] == 0x0b:
            print("                          Cmd Ack  : 0x%02x" % (data[1]))

        elif data[0] == 0x0c:
            print("                          Cmd NAck : 0x%02x" % (data[1]))

        elif data[0] == 0x29:
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
            datastr = ''.join(
                list(map(chr, data[1:struct.calcsize(fmt) + 1])))

            (navval, navtype, ewn, tow, year, month, day, hour, minute,
             second, satlst, latitude, longitude, alt_elip, alt_msl,
             datum, sog, cog, magvar, climbrate, headrate, estHPE, estVPE,
             estTE, estHVE, clockbias, CBerr, clockdrift, CDerr, distance,
             distanceErr, headErr, numsvs, hdop, addmodeinfo
             ) = struct.unpack(fmt, bytes(datastr, 'Latin-1'))

            out = {}
            # GPS time of week (sec)
            out['tow'] = float(tow) / 1e3

            # Seconds
            out['second'] = float(second) / 1e3

            # Latitude/Longitude (degrees)
            out['latitude'] = float(latitude) / 1e7
            out['longitude'] = float(longitude) / 1e7

            # Altitude from ellipsoid (meters)
            out['alt_elip'] = float(alt_elip) / 1e2

            # Altitude from mean sea level (meters)
            out['alt_msl'] = float(alt_msl) / 1e2

            # Speed over ground ("m/s")
            out['sog'] = float(sog) / 1e2  
            
            # Course over ground ("degrees clockwise from true north")
            out['cog'] = float(cog) / 1e2  

            # Climb rate ("m/s")
            out['climbrate'] = float(climbrate) / 1e2  

            # Heading rate ("deg/s")
            out['headrate'] = float(headrate) / 1e2  

            # Estimated horizonal position error (meters)
            out['estHPE'] = float(estHPE) / 1e2  

            # Estimated vertical position error (meters)
            out['estVPE'] = float(estVPE) / 1e2  

            # Estimated time error (seconds)
            out['estTE'] = float(estTE) / 1e2  

            # Estimated horizontal velocity error (m/s)
            out['estHVE'] = float(estHVE) / 1e2  

            # Clock bias ("m")
            out['clockbias'] = float(clockbias) / 1e2 

            # Clock bias error ("meters")
            out['CBerr'] = float(CBerr) / 1e2 

            # Clock drift ("m/s")
            out['clockdrift'] = float(clockdrift) / 1e2 

            # Clock drift error ("m/s")
            out['CDerr'] = float(CDerr) / 1e2 

            # Distance travelled since reset (meters)
            out['distance'] = distance 

            # Distance Error (meters)
            out['distanceErr'] = distanceErr 

            # Heading error (degrees)
            out['headErr'] = float(headErr) / 1e2 

            # Number of sats
            out['numsvs'] = numsvs 

            # Horizontal dilution of precision (.2 resolution)
            out['hdop'] = float(hdop) / 5 

            # Fix type
            out['fixtype'] = fixtype[navtype & 0x7]
            
            # Bitmap of sats used in solution Bit 0 = Sat 1, etc.
            out['satlst'] = satlst 

            # Map datum to which lat, long, alt apply: 21 = WGS-84
            out['datum'] = datum 

            # Magnetic variation [NOT IMPLEMENTED]
            out['magvar'] = magvar 

            out['date'] = '{:02}/{:02}/{:02}'.format(year, month, day)
            out['time'] = '{:02}:{:02}:{:02}'.format(hour, 
                                                     minute, int(second/1e3))

            return out

        elif data[0] == 0x34:
            fmt = '>BBBBBHHIB'
            datastr = ''.join(list(map(chr, data[1:struct.calcsize(fmt) + 1])))

            (hour, minute, second, day, month, year, 
             offsetint, offsetfrac, status
             ) = struct.unpack(fmt, bytes(datastr, 'Latin-1'))

            offset = offsetint + float(offsetfrac) / 1e9
            print(("PPS : %04d/%02d/%02d %02d:%02d:%02d, " + 
                   "Offset : %.9f, Status : 0x%02x") % 
                  (year, month, day, hour, minute, second, offset, status))

        elif data[0] == 0xa6:
            print("Message rate : MID 0x%02x, rate 0x%02x" % 
                  (data[2], data[3]))


def read_sbn(filename):
    with open(filename, 'rb') as f:
        sbn = f.read()
    p = Parser()
    p.process(sbn)
    return p

