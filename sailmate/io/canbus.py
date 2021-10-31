import can
from can.interface import Bus

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 250000

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

## start dumping TODO move this back to main
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


## read from the can_bus

## check if multi-line

## parse to