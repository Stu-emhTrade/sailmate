from subprocess import Popen, PIPE

## start the canbus
canbus_process = Popen(['python3', './sailmate/logger/experiment/canbus.py'],
                       stdin=PIPE,
                       stdout=PIPE)

## pipe to a subprocess that prints it to it's std out (this will be nodejs)
signalk_process = Popen(['python3', './sailmate/logger/experiment/signalk.py'],
                        stdin=canbus_process.stdout,
                        stdout=PIPE)

while True: #check db for stop flag
    ## read signal k
    bob = signalk_process.stdout.readline().decode()
    ## publish to db
    print(bob)

## kill subprocesses