from datetime import datetime
import os
import json
import sqlite3
from db.setup import setup_log_db, setup_app_db
from logger.app import create_app

LOG_DATA_PATH = './sailmate/data/logData/'
APP_DB_FILE = './sailmate/data/app_data.db'

def main():
    ## setup app db
    if not setup_app_db(APP_DB_FILE):
        raise ValueError("app db not setup")

    ## initialise an sqllite file for data
    log_db = setup_log_db(LOG_DATA_PATH)


    app = create_app(APP_DB_FILE, log_db)
    ## run flask app
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()

# ## setup file dump