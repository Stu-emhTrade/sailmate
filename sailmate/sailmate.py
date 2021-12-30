from datetime import datetime
import os
import json
import sqlite3
import argparse
from .db.setup import setup_log_db, setup_app_db
from .logger.app import create_app

LOG_DATA_PATH = './sailmate/data/logData/'
APP_DB_FILE = './sailmate/data/app_data.db'

def main(test_can_file = None):
    ## setup app db
    if not setup_app_db(APP_DB_FILE):
        raise ValueError("app db not setup")

    # initialise an sqllite file for data
    log_db_path = setup_log_db(LOG_DATA_PATH)

    # run flask app
    app = create_app(APP_DB_FILE, log_db_path, test_can_file)
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', action='store', default=None)

    args = parser.parse_args()
    main(test_can_file=args.filename)
    #todo parse sys args

