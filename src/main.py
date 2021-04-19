import can
can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 250000
from can.interface import Bus
from datetime import datetime
import os
import json

def format_msg(can_msg):
    tmp = {"timestamp": can_msg.timestamp,
           "sender_id": can_msg.arbitration_id,
           "dlc": can_msg.dlc,
           "data": list(can_msg.data)}
    return json.dumps(tmp)

def null_msg():
    tmp = {"timestamp": datetime.now().timestamp(),
           "sender_id": None,
           "dlc": None,
           "data": None}
    return json.dumps(tmp)

## setup file dump
today = datetime.now().strftime('%Y%m%d')
files = os.listdir('./logData/')
matching_files = [ i for i, f in enumerate(files) if f.split('_')[0] == today ]
if len(matching_files) > 0:
    new_incr = 1 + max([int(files[i].split('_')[1].split('.')[0]) for i in matching_files])
    filename = today + '_' + str(new_incr) + '.ndjson'
else:
    filename = today + '_0.ndjson'

## start dumping
bus = Bus()
listener = can.BufferedReader()

with open('./logData/' + filename, 'a') as logfile:
    while True:
        msg = bus.recv(timeout=1)
        listener.on_message_received(msg=msg)
        bob = listener.get_message(timeout=0.1)
        if bob:
            logfile.writelines(format_msg(bob) + '\n')
            logfile.flush()
        else:
            logfile.writelines(null_msg() + '\n')
            logfile.flush()




