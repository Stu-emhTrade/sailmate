import sqlite3
import json
import logging
import uuid
from ..pgn.pgn import PgnRecord
from ..io.time_conversion import convert_to_utc
from datetime import datetime

logger = logging.getLogger(__name__)


def set_logging_flag(conn: sqlite3.Connection, value: [int, bool]) -> bool:
    value = int(value)
    c = conn.cursor()

    c.execute("""UPDATE logging
                 SET run_log = :val
                 WHERE id = 1""",
              {"val": value})

    conn.commit()

    tmp = c.execute("""SELECT run_log 
                       FROM logging 
                       WHERE id = 1""").fetchall()

    return bool(tmp[0][0])


def get_logging_flag(conn: sqlite3.Connection) -> bool:
    c = conn.cursor()
    tmp = c.execute(
            """SELECT run_log 
            FROM logging 
            WHERE id = 1""").fetchall()

    return bool(tmp[0][0])


def get_current_voyage_id(conn: sqlite3.Connection) -> str:
    c = conn.cursor()
    c.execute("""SELECT voyage_id, start_datetime
                FROM voyage 
                WHERE end_datetime is null
                ORDER BY start_datetime desc""")

    open_voyages = c.fetchall()

    if len(open_voyages) > 1:
        logger.warning(f'multiple voyages open: {open_voyages}')

    if len(open_voyages) == 0:
        return None
    else:
        return open_voyages[0][0]


def insert_voyage(conn: sqlite3.Connection, record: dict) -> str:
    record['voyage_id'] = str(uuid.uuid4())
    print(record)
    c = conn.cursor()
    c.execute("""INSERT INTO voyage (
                        voyage_id,
                        name, 
                        start_datetime, 
                        sail_wardrobe, 
                        voyage_type,
                        pob)
                        VALUES (:voyage_id, 
                                :voyage_name, 
                                :start_datetime, 
                                :sail_wardrobe, 
                                :voyage_type, 
                                :pob)""",
              record)

    conn.commit()

    voyage_id = get_current_voyage_id(conn)
    logger.info(f'inserted voyage_id: {voyage_id}')

    return voyage_id


def insert_voyage_end(conn: sqlite3.Connection, voyage_id: str):
    c = conn.cursor()
    c.execute("""UPDATE voyage
                SET end_datetime = :end_dt
                WHERE voyage_id = :vi""",
              {"end_dt": convert_to_utc(datetime.now()),
               "vi": voyage_id}
              )

    conn.commit()


def insert_log_filename(conn: sqlite3.Connection,
                        voyage_id: str,
                        filename: str):
    c = conn.cursor()
    print(f'vi: {voyage_id} fn: {filename}')
    c.execute("""UPDATE voyage
                 SET log_filename = :fn
                 WHERE voyage_id = :vi""",
              {"fn": filename,
               "vi": voyage_id}
              )

    conn.commit()


def get_log_filename(conn: sqlite3.Connection,
                     voyage_id: str) -> str:
    c = conn.cursor()

    c.execute("""SELECT log_filename
                 FROM voyage 
                 WHERE voyage_id = :vi""",
              {"vi": voyage_id})

    filename = c.fetchone()[0]

    return filename


def insert_pgns(conn: sqlite3.Connection, pgn_records: [PgnRecord]):
    c = conn.cursor()

    for p in pgn_records:
        telemetry_records = p.unpack()
        telemetry_tuples = [x.as_tuple() for x in telemetry_records]

        sql = """INSERT INTO telemetry 
                 (timestamp, pgn, variable_name, value)
                 VALUES (?, ?, ?, ?)"""
        c.executemany(sql, telemetry_tuples)

    conn.commit()


def get_current_sail_config(conn: sqlite3.Connection) -> dict:
    c = conn.cursor()

    sql = """SELECT value
            FROM telemetry
            where variable_name = 'sailConfig'
            AND timestamp = (
                    SELECT timestamp
                    FROM telemetry
                    WHERE variable_name = 'sailConfig'
                    order by timestamp desc
                    limit 1)"""
    tmp = c.execute(sql).fetchone()
    if tmp is None:
        tmp = {
                'main_sail': None,
                'head_sail': None,
                'flying_sail': None
                }

    else:
        tmp = json.loads(tmp[0])

    return tmp


def log_sail_config(conn: sqlite3.Connection, value: dict):
    c = conn.cursor()

    ts = convert_to_utc(datetime.now())

    variable_name = 'sailConfig'
    value = json.dumps(value)

    sql = """INSERT INTO telemetry
             (timestamp, pgn, variable_name, value)
             VALUES (strftime('%Y-%m-%d %H:%M:%f',?), null, ?, ?)"""

    c.execute(sql, (ts, variable_name, value))

    conn.commit()


def get_voyage_wardrobe(conn: sqlite3.Connection) -> dict:
    # TODO this needs to look at a voyage table in app_db
    # Voyage table should be a subset of a vessel wardrobe. user needs to be able to add/remove these

    sails_onboard = {
            'main_sails': [None, 'full_main', 'reef_1', 'reef_2', 'reef_3'],
            'head_sails': [None, 'genoa', 'j_2', 'j_2.5', 'j_3', 'j_4'],
            'flying_sails': [None, 'a1', 'a2', 'a4', 'fr0']
            }

    return sails_onboard


def get_log_db_conn(log_db_path: str,
                    app_db_conn: sqlite3.Connection,
                    voyage_id: str
                    ) -> sqlite3.Connection:
    log_db_filename = get_log_filename(app_db_conn, voyage_id)
    db_file = log_db_path + log_db_filename
    logger.info(f'retrieved db filename: {db_file}')
    db_conn = sqlite3.Connection(db_file, check_same_thread=False)

    return db_conn
