import pytz
from datetime import datetime
import json
import subprocess


def parse_can_id(id):
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


def convert_timestamp(ts):
    nzt = pytz.timezone('Pacific/Auckland')  # TODO this needs attention for other locales.
    ts = datetime.fromtimestamp(ts)
    ts = nzt.localize(ts).astimezone(pytz.utc)
    return "%s:%06.3f%s" % (
        ts.strftime('%Y-%m-%dT%H:%M'),
        float("%06.3f" % (ts.second + ts.microsecond / 1e6)),
        'Z')


def convert_to_actisense(r):
    # timestamp,prio,pgn,src,dst,len,data
    output = {}
    output['timestamp'] = convert_timestamp(r['timestamp'])
    tmp = parse_can_id(r['sender_id'])

    return ",".join([convert_timestamp(r['timestamp']),
                     str(tmp['prio']),
                     str(tmp['pgn']),
                     str(tmp['src']),
                     str(tmp['dst']),
                     str(r['dlc']),
                     ",".join([format(i, 'x').zfill(2) for i in r['data']])])


def canboat_convert():
    shell_command = f'cat ./data/logData/actisenseTest.csv | analyzerjs | ../../n2k-signalk/bin/n2k-signalk --flat'

    converted_data = subprocess.run(shell_command,
                                    shell=True,
                                    stdout=subprocess.PIPE).stdout

    with open('./data/logData/signalkTest.ndjson', 'w') as jsonFile:
        jsonFile.write(converted_data.decode('utf-8'))


def make_actisense_from_test_dat():
    with open('./data/logData/testFile.ndjson') as infile:
        with open('./data/logData/actisenseTest.csv', 'w') as outfile:
            outfile.truncate(0)
            for i in infile:
                input_line = infile.readline()
                if (len(input_line) == 0):
                    break
                else:
                    line_to_write = convert_to_actisense(json.loads(input_line)) + '\n'

                outfile.write(line_to_write)


