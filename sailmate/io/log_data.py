from subprocess import Popen, PIPE

## start the canbus
canbus_process = Popen(['python3', './sailmate/io/canbus.py', '--filename=./sailmate/data/logData/actisenseTest.csv'],
                       stdout=PIPE)

## pipe to a subprocess that prints it to it's std out (this will be nodejs)
signalk_process = Popen(['analyzerjs', '|', 'n2k-signalk', '--flat'],
                        stdin=canbus_process.stdout,
                        stdout=PIPE)

with signalk_process.stdout as sigK:
    for i in sigK:
        print(i)


while True: #check db for stop flag
    ## read signal k
    bob = signalk_process.stdout.readline().decode()
    ## publish to db
    print(bob)

## kill subprocesses


signalk_data = subprocess.run('analyserjs | n2k-signalk --flat',
                              stdout=subprocess.PIPE).stdout

