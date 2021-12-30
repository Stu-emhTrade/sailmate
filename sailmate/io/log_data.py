from subprocess import Popen, PIPE, STDOUT
import json
from ..logger.pgn import pgn_handler
from ..logger.pgn_model import pgn_model
from ..db.functions import get_logging_flag


def log_data(conn, filename=None):
    canbus_args = ['python3', './sailmate/io/canbus.py']
    if filename:
        canbus_args.append(f'--filename={filename}')
    ## start the canbus
    canbus_process = Popen(canbus_args,
                           stdout=PIPE)

    ## pipe to a subprocess that prints it to it's std out (this will be nodejs)
    signalk_process = Popen(['actisense-signalk'],
                            stdin=canbus_process.stdout,
                            stdout=PIPE,
                            stderr=STDOUT)

    ## todo ^^ maybe instead of piping from one to other, could check if we want to keep the pgn or not first.

    keep_logging = True

    while keep_logging:

        for i in range(100):
            ## read signal k
            tmp_line = signalk_process.stdout.readline().decode()
            try:
                tmp_line = json.loads(tmp_line)
                pgns = pgn_handler(tmp_line, pgn_model)  # this is a list, could be length 0

                # for pgns db insert
                print(i)
                for p in pgns:
                    print(p)
            except json.decoder.JSONDecodeError as e:
                print(i)
                print(e)
                continue

        keep_logging = get_logging_flag(conn)

    ## kill subprocesses
    canbus_process.kill()
    signalk_process.kill()


if __name__ == '__main__':
    log_data(conn='../data/logData/testdb.db',
             filename='../data/logData/actisenseTest.csv')
