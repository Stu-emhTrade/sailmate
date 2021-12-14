filepath = './logData/'
filename = '20210423_0.ndjson'


def add_filename(dat, fn):
    tmp = json.loads(dat)
    tmp['data_file'] = fn
    return json.dumps(tmp)


with open(filepath + filename) as f:
    with open('./logData/testFile.ndjson', 'w') as outfile:
        for i in range(1000000):
            outfile.write(f.readline())

# Decode CAN Identifier (canId). ISO 11783 (CAN 2.0 B Extended Frame Format)


import json
import subprocess


with open('./logData/testFile.ndjson') as infile:
    with open('./logData/actisenseTest.csv', 'w') as outfile:
        outfile.truncate(0)
        for i in infile:
            line_to_write = convert_to_actisense(json.loads(infile.readline())) + '\n'
            outfile.write(line_to_write)

# todo pipe the testFile straight to the converter using naked.

with open('./logData/canboatJSON_test.ndjson', 'w') as jsonFile:  # todo deal with stderr so it doesn't clog memory
    process = subprocess.Popen('cat ./logData/actisenseTest.csv | analyzerjs',
                               shell=True,
                               stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            jsonFile.write(output)
            jsonFile.flush()
        rc = process.poll()

signalk_data = subprocess.run('cat ./logData/actisenseTest.csv | analyzerjs | n2k-signalk --flat',
                              shell=True,
                              stdout=subprocess.PIPE).stdout

with open('./logData/signalk_test.ndjson', 'w') as jsonFile:
    jsonFile.write(signalk_data.decode('utf-8'))


signalk_data = subprocess.run('analyserjs | n2k-signalk --flat',
                              stdout=subprocess.PIPE).stdout

