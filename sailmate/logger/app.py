import sqlite3
from flask import Flask
import threading
import time
from ..db.functions import set_logging_flag
from ..io.log_data import log_data
import json
import os


def create_app(
        app_db: str,
        log_db: str,
        test_can_file: [str, None] = None) -> Flask:

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

        if test_can_file is None:
            log_thread = threading.Thread(target=log_data,
                                          args=[log_db_conn])

        else:
            log_thread = threading.Thread(target=log_data,
                                          args=[log_db_conn],
                                          kwargs={'filename': test_can_file})
        log_thread.start()

        return json.dumps({"logger_running": logging_flag})

    @app.route("/stop_log")
    def stop_log():
        print('stopping log')

        app_db_conn = sqlite3.Connection(app_db)
        logging_flag = set_logging_flag(app_db_conn, False)

        app_db_conn.close()
        return json.dumps({"logger_running": logging_flag})

    return app

