import pytz
from datetime import datetime
import math
import json
import argparse


def parseCanId(id):
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


def convertTimeStamp(ts):
    nzt = pytz.timezone('Pacific/Auckland')  # TODO this needs attention for other locales.
    ts = datetime.fromtimestamp(ts)
    ts = nzt.localize(ts).astimezone(pytz.utc)

    ts_microseconds = math.floor(ts.microsecond/1000)

    ts_seconds = float("%06.3f" % (ts.second + (ts_microseconds / 1000)))

    return "%s:%06.3f%s" % (
        ts.strftime('%Y-%m-%dT%H:%M'),
        ts_seconds,
        'Z')


def convertToActisense(r):
    # timestamp,prio,pgn,src,dst,len,data
    output = {}
    output['timestamp'] = convertTimeStamp(r['timestamp'])
    tmp = parseCanId(r['sender_id'])

    return ",".join([convertTimeStamp(r['timestamp']),
                     str(tmp['prio']),
                     str(tmp['pgn']),
                     str(tmp['src']),
                     str(tmp['dst']),
                     str(r['dlc']),
                     ",".join([format(i, 'x').zfill(2) for i in r['data']])])


def main(input_filename, output_filename):
    with open(input_filename) as infile:
        with open(output_filename, 'w') as outfile:
            outfile.truncate(0)
            for i in infile:
                line_to_write = convertToActisense(json.loads(infile.readline())) + '\n'
                outfile.write(line_to_write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_filename', action='store', default=None)
    parser.add_argument('--output_filename', action='store', default=None)

    args = parser.parse_args()
    main(input_filename=args.input_filename,
         output_filename=args.output_filename)