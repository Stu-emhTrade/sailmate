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
    insert_voyage,
    insert_voyage_end,
    insert_log_filename,
    get_log_db_conn
    )

from sailmate.db.setup import setup_log_db
from sailmate.io import time_conversion
from sailmate.io.log_data import log_data

logger = logging.getLogger(__name__)


def create_app(
        app_db: str,
        log_db_path: str,
        test_can_file: [str, None] = None) -> Flask:
    app = Flask(__name__)

    app_db_conn = sqlite3.Connection(app_db, check_same_thread=False)

    @app.route("/<int:voyage_id>")
    def index(voyage_id: [int, None] = None):
        if not voyage_id:
            voyage_id = get_current_voyage_id(app_db_conn)
            if not voyage_id:
                return render_template('voyage_form.html')
        logging_flag = get_logging_flag(app_db_conn)
        return render_template('index.html', logging_flag=logging_flag)

    @app.route("/voyage/start", methods=['PUT'])
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
        log_filename = datetime.now().strftime('%Y%m%d') + '_' + str(voyage_id) + '.db'
        insert_log_filename(app_db_conn, voyage_id, log_filename)

        # setup the log db with the log_filename
        if setup_log_db(log_db_path + log_filename):
            logger.info(f'created log db: {log_filename}')
            return redirect(url_for('index', voyage_id=voyage_id))
        # return the voyage id and pass that around with html (hidden)
        else:
            logger.error(f'log_db not created for voyage {voyage_id}')
            raise ValueError(f'log_db not created for voyage {voyage_id}')

    @app.route("/voyage/end", methods=['POST'])  #unsure on whether v_id should be an endpoint param rather than from
    # or request field. Aim for consistency with sail wardrobe & logger
    def end_voyage():
        set_logging_flag(app_db_conn, value=False)  # refactor to use log/stop endpoint

        voyage_id = request.form.get('voyage_id', type=int)
        if not voyage_id:
            logger.error('no voyage_id supplied to voyage/end')
            raise ValueError('no voyage_id supplied to voyage/end')

        insert_voyage_end(app_db_conn, voyage_id)

        return redirect(url_for('index', voyage_id=None))

    #todo /voyage/edit eg to fix an iput error (wardrobe, type, name etc)


    @app.route("/start_log", methods=['POST'])
    def start_log():
        voyage_id = request.form.get('voyage_id', type=int)

        log_db_conn = get_log_db_conn(log_db_path,
                                      app_db_conn,
                                      voyage_id)

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

        return redirect(url_for('index', voyage_id=voyage_id))

    @app.route("/stop_log")
    def stop_log():
        voyage_id = request.form.get('voyage_id', type=int)
        set_logging_flag(app_db_conn, False)
        logger.info('logger flag set to false')
        return redirect(url_for('index', voyage_id=voyage_id))

    @app.route("/sail_change", methods=['POST', 'GET'])
    def sail_change():

        sail_change_db_conn = sqlite3.Connection(log_db)
        if request.method == 'GET':
            sail_config = get_current_sail_config(sail_change_db_conn)

            wardrobe = get_voyage_wardrobe(sail_change_db_conn)
            # todo refactor to voyage endpoint

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
