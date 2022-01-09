import sqlite3
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import threading
from sailmate.db.functions import (
    set_logging_flag,
    get_logging_flag,
    get_current_sail_config,
    log_sail_config,
    get_voyage_wardrobe,
    insert_voyage
    )

from sailmate.io import time_conversion

from sailmate.io.log_data import log_data

logger = logging.getLogger(__name__)


def create_app(
        app_db: str,
        log_db_path: str,
        test_can_file: [str, None] = None) -> Flask:
    app = Flask(__name__)

    app_db_conn = sqlite3.Connection(app_db, check_same_thread=False)

    @app.route("/")
    def index():
        logging_flag = get_logging_flag(app_db_conn)
        return render_template('index.html', logging_flag=logging_flag)

    @app.route("/voyage", methods=['PUT'])
    def create_voyage():
        record = {'name': request.form.get('name'),
                  'start_datetime': time_conversion.convert_to_utc(datetime.now()),
                  'end_datetime': None,
                  'log_filename': None,
                  'sail_wardrobe TEXT,'
                  'voyage_type': request.form.get('voyage_type'),
                  'pob': request.form.get('pob'),
                  'uploaded_datetime': None}

        # insert a record, warning if previous record still open
        voyage_id = insert_voyage(app_db_conn, record)

        # create a logfile name from date and voyage_id insert that
        log_filename = datetime.now().strftime('%Y%m%d') + '_' + str(voyage_id)

        # setup the log db with the log_filename
        

        # return the voyage id and pass that around with html (hidden)


    @app.route("/start_log", methods=['POST'])
        #todo pass the logfile into here from the request (form or json??)
    def start_log():
        log_db = request.form.get('log_filename')
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

        logger.info('starting data logging thread')
        log_thread.start()

        return redirect(url_for('index'))

    @app.route("/stop_log")
    def stop_log():
        set_logging_flag(app_db_conn, False)
        logger.info('logger flag set to false')
        return redirect(url_for('index'))

    @app.route("/sail_change", methods=['POST', 'GET'])
    def sail_change():

        sail_change_db_conn = sqlite3.Connection(log_db)
        if request.method == 'GET':
            sail_config = get_current_sail_config(sail_change_db_conn)

            wardrobe = get_voyage_wardrobe(sail_change_db_conn)
            #todo refactor to voyage endpoint

            return render_template('sail_change.html',
                                   sail_config=sail_config,
                                   sail_wardrobe=wardrobe)

        else:
            sail_config = {
                'main_sail': request.form.get('main_sail'),
                'head_sail': request.form.get('head_sail'),
                'flying_sail': request.form.get('flying_sail')
            }

            logger.info('logging sail change')
            log_sail_config(sail_change_db_conn, sail_config)

            return redirect(url_for('index'))

    return app
