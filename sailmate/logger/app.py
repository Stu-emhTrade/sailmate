import sqlite3
from flask import Flask
import threading
import time
# from logger.parsers import make_actisense_from_test_dat, canboat_convert
from ..db.functions import set_logging_flag
# from io.canbus import start_canbus
import json
import os


def create_app(app_db: str,
        log_db: str) -> Flask:

    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello World!"

    @app.route("/start_log")
    def start_log():
        print('starting to log')

        app_db_conn = sqlite3.Connection(app_db)
        logging_flag = set_logging_flag(app_db_conn, True)
        app_db_conn.close()
        # x = threading.Thread(target=log_nmea_data,
        #                      args=[log_db])
        # x.start()
        #
        # canboat_convert()

        return json.dumps({"logger_running": logging_flag})

    @app.route("/stop_log")
    def stop_log():
        print('stopping log')

        app_db_conn = sqlite3.Connection(app_db)
        logging_flag = set_logging_flag(app_db_conn, False)

        app_db_conn.close()
        return json.dumps({"logger_running": logging_flag})

    return app
