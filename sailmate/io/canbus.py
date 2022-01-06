import sys
import can
import pytz
import math
import argparse
from datetime import datetime
from dataclasses import dataclass


can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 250000


from can.interface import Bus


@dataclass
class NmeaMessage:
    timestamp: float
    arbitration_id: int
    dlc: int
    data: bytearray

    def convert_timestamp(self):
        ts = self.timestamp
        nzt = pytz.timezone('Pacific/Auckland')  # TODO this needs attention for other locales.
        ts = datetime.fromtimestamp(ts)
        ts = nzt.localize(ts).astimezone(pytz.utc)

        ts_microseconds = math.floor(ts.microsecond / 1000)

        ts_seconds = float("%06.3f" % (ts.second + (ts_microseconds / 1000)))

        return "%s:%06.3f%s" % (
            ts.strftime('%Y-%m-%dT%H:%M'),
            ts_seconds,
            'Z')

    def parse_can_id(self) -> {int}:
        id = self.arbitration_id
        res = {'canId': id,
               'prio': ((id >> 26) & 0x7),
               'src': id & 0xff,
               'PF': (id >> 16) & 0xff,
               'PS': (id >> 8) & 0xff,
               'DP': (id >> 24) & 1,
               'EDP': (id >> 25) & 1}

        if res['PF'] < 240:
            # PDU1 format, the PS contains the destination address
            res['dst'] = res['PS']
            res['pgn'] = (res['DP'] << 16) + (res['PF'] << 8)
        else:
            # PDU2 format, the destination is implied global and the PGN is extended
            res['dst'] = 0xff
            res['pgn'] = (res['DP'] << 16) + (res['PF'] << 8) + res['PS']
        return res

    def convert_to_actisense(self) -> str:
        # timestamp,prio,pgn,src,dst,len,data
        tmp = self.parse_can_id()

        return ",".join([self.convert_timestamp(),
                         str(tmp['prio']),
                         str(tmp['pgn']),
                         str(tmp['src']),
                         str(tmp['dst']),
                         str(self.dlc),
                         ",".join([format(i, 'x').zfill(2) for i in self.data])])


def read_canbus(filename=None):

    if filename is None:
        bus = Bus()
        listener = can.BufferedReader()
        while True:
            msg = bus.recv(timeout=1)
            listener.on_message_received(msg=msg)
            tmp_msg = listener.get_message(timeout=0.1)
            if tmp_msg:
                nmea_msg = NmeaMessage(tmp_msg.timestamp,
                                       tmp_msg.arbitration_id,
                                       tmp_msg.dlc,
                                       tmp_msg.data)
                sys.stdout.writelines(nmea_msg.convert_to_actisense())

    else:
        with open(filename) as test_file:
            for line in test_file:
                sys.stdout.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', action='store', default=None)
    args = parser.parse_args()

    read_canbus(args.filename)




