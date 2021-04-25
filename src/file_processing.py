
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


# Connection to the AWS IoT Core with Root CA certificate and unique device credentials (keys and certificate) previously retrieved
ENDPOINT = 'az2cr6o11vm1o-ats.iot.ap-southeast-2.amazonaws.com'
ROOT_CA = './../.private/Amazon-root-CA-1.pem'
DEVICE_CERT = './../.private/device.pem.crt'
PRIVATE_KEY = './../.private/private.pem.key'
# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("BoatPi")
# For TLS mutual authentication
myMQTTClient.configureEndpoint(ENDPOINT,8883)  # Provide your AWS IoT Core endpoint (Example: "abcdef12345-ats.iot.us-east-1.amazonaws.com")
myMQTTClient.configureCredentials(ROOT_CA, PRIVATE_KEY,DEVICE_CERT)  # Set path for Root CA and unique device credentials (use the private key and certificate retrieved from the logs in Step 1)
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

myMQTTClient.connect()

filepath = './logData/'
filename = 'testFile.ndjson' ## todo add user input to display and select a file

with open(filepath + filename) as f:
    for l in f:
        msg = l ## todo add filename, handle multi-line msg
        myMQTTClient.publish("NMEA_data", msg, 0)

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