import os
from datetime import datetime
import sqlite3

def get_db_filename(log_data_path: str) -> str:
    today = datetime.now().strftime('%Y%m%d')
    files = os.listdir(log_data_path)
    matching_files = [i for i, f in enumerate(files) if f.split('_')[0] == today]
    if len(matching_files) > 0:
        new_incr = 1 + max([int(files[i].split('_')[1].split('.')[0]) for i in matching_files])
        filename = today + '_' + str(new_incr) + '.db'
    else:
        filename = today + '_0.db'

    return filename


def setup_log_db(log_data_path: str) -> str:
    filename = get_db_filename(log_data_path)
    conn = sqlite3.connect(log_data_path + filename)
    #TODO: some stuff here to initialise the data tables
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
    # todo put this file in the app db? could include date, filename, uploaded
    return log_data_path + filename



def setup_app_db(app_db_filename: str) -> bool:
    print(os.getcwd() + app_db_filename)
    conn = sqlite3.connect(app_db_filename)
    c = conn.cursor()

    create_query = ('CREATE TABLE IF NOT EXISTS logging '
                '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'run_log INTEGER)')

    initial_value_query = ('INSERT INTO logging(id, run_log) '
                       'VALUES(1, 0) '
                       'ON CONFLICT(id) DO '
                       'UPDATE SET run_log = FALSE')

    c.execute(create_query)
    c.execute(initial_value_query)

    conn.commit()
    return True



