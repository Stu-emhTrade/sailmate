import can
from can.interface import Bus
import sys
import json
from ..db.functions import get_logging_flag, insert_telemetry_records

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 250000



def start_canbus():
    bus = Bus()
    listener = can.BufferedReader()
    while True:
        msg = bus.recv(timeout=1)
        listener.on_message_received(msg=msg)
        tmp_msg = listener.get_message(timeout=0.1)
        if tmp_msg:
            sys.stdout.write(tmp_msg)


def log_nmea_data(conn: sqlite3.Connection):
    while get_logging_flag(conn):
        counter = 0

        ### read the can bus
        # each line,convert to actisense:
        #   convert_to_actisense(format_msg(l))
        # stream to analyserjs

        ### read to the signalk stream
        ## convert to PgnRecord
        # if a record add to counter, send insert statement
        # if not next
        # if counter = 100, commit transaction

        ### every 10 seconds or so, check the db to see if the logging period is ended.


## read from the can_bus

## check if multi-line

## parse to
