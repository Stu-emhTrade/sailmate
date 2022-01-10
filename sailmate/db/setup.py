import os
import logging
from datetime import datetime
import sqlite3
from sailmate.db.functions import (
    get_log_filename
    )

logger = logging.getLogger(__name__)

# todo take voyage start date as date arg rather than now
# def get_db_filename(
#         log_data_path: str,
#         voyage_start: datetime) -> str:
#
#     voyage_date = voyage_start.strftime('%Y%m%d')
#     files = os.listdir(log_data_path)
#     matching_files = [i for i, f in enumerate(files) if f.split('_')[0] == voyage_date]
#     if len(matching_files) > 0:
#         new_incr = 1 + max([int(files[i].split('_')[1].split('.')[0]) for i in matching_files])
#         filename = voyage_date + '_' + str(new_incr) + '.db'
#     else:
#         filename = voyage_date + '_0.db'
#
#     return filename


def setup_log_db(file: str) -> str:

    conn = sqlite3.connect(file)
    c = conn.cursor()

    create_script = ('CREATE TABLE IF NOT EXISTS telemetry '
                     '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                     'timestamp TEXT,'
                     'pgn INTEGER,'
                     'variable_name TEXT,'
                     'value REAL); '
                     'CREATE INDEX idx_telemetry_timestamp '
                     'ON telemetry (timestamp); '
                     'CREATE INDEX idx_telemetry_variable '
                     'ON telemetry (variable_name); '
                     'CREATE INDEX idx_telemetry_pgn '
                     'ON telemetry (pgn);')

    c.executescript(create_script)

    conn.commit()
    return True


def setup_app_db(app_db_filename: str) -> bool:
    conn = sqlite3.connect(app_db_filename)
    c = conn.cursor()

    create_query = ('CREATE TABLE IF NOT EXISTS logging '
                    '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    'run_log INTEGER);'

                    'CREATE TABLE IF NOT EXISTS voyage '
                    '(voyage_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                    'name TEXT,'
                    'log_filename TEXT,'
                    'start_datetime TEXT,'
                    'end_datetime TEXT,'
                    'sail_wardrobe TEXT,'
                    'pob INTEGER,'
                    'voyage_type TEXT,'
                    'uploaded_datetime TEXT);'

                    'CREATE INDEX IF NOT EXISTS idx_voyage_start '
                    'ON voyage (start_datetime); '

                    'CREATE INDEX IF NOT EXISTS idx_voyage_end '
                    'ON voyage (end_datetime); '
                    )

    initial_value_query = ('INSERT INTO logging(id, run_log) '
                           'VALUES(1, 0) '
                           'ON CONFLICT(id) DO '
                           'UPDATE SET run_log = FALSE')

    c.executescript(create_query)
    c.execute(initial_value_query)

    conn.commit()
    return True
