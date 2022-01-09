import sqlite3
import json
from ..pgn.pgn import PgnRecord
from ..io.time_conversion import convert_to_utc
from datetime import datetime


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


def insert_voyage(conn: sqlite3.Connection, record: dict) -> int:
    c = conn.cursor()
    voyage_id = c.fetchone("""INSERT INTO voyage (name, 
                        start_datetime, 
                        sail_wardrobe, 
                        voyage_type,
                        pob)
                        VALUES (:name, :start_datetime, :sail_wardrobe, :pob)
                        RETURNING voyage_id""",
                          record)
    conn.commit()

    # todo check that there's now only one voyage with no end_date

    return voyage_id


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
