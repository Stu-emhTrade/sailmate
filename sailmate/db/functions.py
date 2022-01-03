import sqlite3
from ..logger.pgn import PgnRecord


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


def insert_pgns(conn: sqlite3.Connection, pgn_records: [PgnRecord]):
    c = conn.cursor()

    for p in pgn_records:
        telemetry_records = p.unpack()
        telemetry_tuples = [x.as_tuple() for x in telemetry_records]

        sql = """INSERT INTO telemetry 
                 (timestamp, pgn, variable_name, value)
                 VALUES (?, ?, ?, ?)"""
        c.executemany(sql, telemetry_tuples)
        print(telemetry_records)

    conn.commit()
