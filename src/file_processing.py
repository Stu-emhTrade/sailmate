import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Connection to the AWS IoT Core with Root CA certificate and unique device credentials (keys and certificate) previously retrieved
ENDPOINT = 'az2cr6o11vm1o-ats.iot.ap-southeast-2.amazonaws.com'
ROOT_CA = './../.private/Amazon-root-CA-1.pem'
DEVICE_CERT = './../.private/device.pem.crt'
PRIVATE_KEY = './../.private/private.pem.key'

filepath = './logData/'
filename = 'testFile.ndjson'  ## todo add user input to display and select a file

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

def createMsgFromRow(r, file = filename):
    tmp = json.loads(r)
    msg = {'data_file': file,
           'pgn': parseCanId(tmp['sender_id'])['pgn'],
           'timestamp': tmp['timestamp'],
           'data': tmp['data']}
    return msg
# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("BoatPi")
# For TLS mutual authentication
myMQTTClient.configureEndpoint(ENDPOINT,
                               8883)  # Provide your AWS IoT Core endpoint (Example: "abcdef12345-ats.iot.us-east-1.amazonaws.com")
myMQTTClient.configureCredentials(ROOT_CA, PRIVATE_KEY,
                                  DEVICE_CERT)  # Set path for Root CA and unique device credentials (use the private key and certificate retrieved from the logs in Step 1)
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

myMQTTClient.connect()

with open(filepath + filename) as f:
    prev_row = {'pgn': None}
    for r in f:
        new_row = createMsgFromRow(r)
        if new_row['pgn'] == prev_row['pgn'] and new_row['data'][0] == (prev_row['data'][0] + 1): # next row of a multiline msg
            msg['data'].extend(new_row['data'])
        else:
            if msg:
                myMQTTClient.publish(str(msg['pgn']), json.dumps(msg), 0) #publish previous
            msg = new_row # put current in buffer
        prev_row = new_row
    myMQTTClient.publish(str(msg['pgn']), json.dumps(msg), 0)




# filepath = './logData/'
# filename = '20210423_0.ndjson'
#
# def add_filename(dat,fn):
#     tmp = json.loads(dat)
#     tmp['data_file'] = fn
#     return json.dumps(tmp)
#
# with open(filepath + filename) as f:
#     with open('./logData/testFile.ndjson', 'w') as outfile:
#         for i in range(100000):
#             outfile.write(f.readline())

# Decode CAN Identifier (canId). ISO 11783 (CAN 2.0 B Extended Frame Format)

