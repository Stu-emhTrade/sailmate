import sqlite3
from ..logger.pgn import TelemetryRecord


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
    tmp = c.execute("""SELECT run_log 
                           FROM logging 
                           WHERE id = 1""").fetchall()

    return bool(tmp[0][0])

def insert_telemetry_records(conn: sqlite3.Connection, pgn_record: [TelemetryRecord]):
    c = conn.cursor()
    sql = """INSERT INTO telemetry 
             VALUES (?, ?, ?, ?)"""
    c.executemany(sql, pgn_record)
