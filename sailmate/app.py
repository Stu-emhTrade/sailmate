import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import threading
import time
from sailmate.db.functions import set_logging_flag, get_logging_flag, get_current_sail_config, log_sail_config, \
    get_voyage_wardrobe

from sailmate.io.log_data import log_data
import json
import os


def create_app(
        app_db: str,
        log_db: str,
        test_can_file: [str, None] = None) -> Flask:
    app = Flask(__name__)

    app_db_conn = sqlite3.Connection(app_db, check_same_thread=False)

    @app.route("/")
    def index():
        logging_flag = get_logging_flag(app_db_conn)

        return render_template('index.html', logging_flag=logging_flag)

    @app.route("/start_log")
    def start_log():
        log_db_conn = sqlite3.Connection(log_db, check_same_thread=False)

        set_logging_flag(app_db_conn, True)

        if test_can_file is None:
            log_thread = threading.Thread(target=log_data,
                                          args=[app_db_conn,
                                                log_db_conn])

        else:
            log_thread = threading.Thread(target=log_data,
                                          args=[app_db_conn,
                                                log_db_conn],
                                          kwargs={'filename': test_can_file})
        log_thread.start()

        return redirect(url_for('index'))

    @app.route("/stop_log")
    def stop_log():
        set_logging_flag(app_db_conn, False)
        return redirect(url_for('index'))

    @app.route("/sail_change", methods=['POST', 'GET'])
    def sail_change():

        sail_change_db_conn = sqlite3.Connection(log_db)
        if request.method == 'GET':
            sail_config = get_current_sail_config(sail_change_db_conn)

            wardrobe = get_voyage_wardrobe(sail_change_db_conn)

            return render_template('sail_change.html',
                                   sail_config=sail_config,
                                   sail_wardrobe=wardrobe)

        else:
            sail_config = {
                'main_sail': request.form.get('main_sail'),
                'head_sail': request.form.get('head_sail'),
                'flying_sail': request.form.get('flying_sail')
            }

            log_sail_config(sail_change_db_conn, sail_config)

            return redirect(url_for('index'))

    return app
