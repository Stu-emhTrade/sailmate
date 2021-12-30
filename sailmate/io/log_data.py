from subprocess import Popen, PIPE, STDOUT
import json
import sqlite3
import os
from ..logger.pgn import pgn_handler
from ..logger.pgn_model import pgn_model
from ..db.functions import get_logging_flag, insert_pgns


def log_data(
        app_db_conn,
        log_db_conn,
        filename=None):

    canbus_cmd_args = ['python3', './sailmate/io/canbus.py']

    if filename:
        canbus_cmd_args.append(f'--filename={filename}')
    # start the canbus
    canbus_process = Popen(canbus_cmd_args,
                           stdout=PIPE)

    # pipe to a subprocess that prints it to it's std out (this will be nodejs)
    signalk_process = Popen(['actisense-signalk'],
                            stdin=canbus_process.stdout,
                            stdout=PIPE,
                            stderr=STDOUT)

    # todo ^^ maybe instead of piping from one to other, could check if we want to keep the pgn or not first.

    keep_logging = True

    while keep_logging:
        pgns_to_insert = []
        for i in range(100):
            # read signal k
            tmp_line = signalk_process.stdout.readline().decode()
            try:
                tmp_line = json.loads(tmp_line)
                pgns = pgn_handler(tmp_line, pgn_model)  # this is a list, could be length 0
                print(i) #todo remove
                for p in pgns:
                    pgns_to_insert.append(p)
                    print(p) # todo remove
            except json.decoder.JSONDecodeError as e:
                print(i)
                print(e)
                continue

        insert_pgns(log_db_conn, pgns_to_insert)

        keep_logging = get_logging_flag(app_db_conn)

    # kill subprocesses
    canbus_process.kill()
    signalk_process.kill()


if __name__ == '__main__':
    print(os.getcwd())
    log_data(app_db_conn=sqlite3.Connection('./sailmate/data/app_data.db'),
             log_db_conn=sqlite3.Connection('./sailmate/data/logData/test/test_log.db'),
             filename='./sailmate/data/logData/test/actisenseTest.csv')
