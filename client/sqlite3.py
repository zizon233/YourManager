import sys
import sqlite3
import logging

sys.path.append("../")

import common

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(common.get_file_handler())


class SQLITE3:
    def __enter__(self):
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        return self

    def connect(self):
        conn = sqlite3.connect("./data/yourmanager.db")
        return conn

    def insert_new_message(self, time, user_id, room_id, message):
        qry = f"INSERT INTO chat VALUES (?, ? , ?, ?)"
        self.cursor.execute(qry, (time, user_id, sqlite3.Binary(room_id), message))
        self.conn.commit()

    def get_all_message(self, room_id):
        qry = f"SELECT * FROM chat ORDER BY time ASC"
        result = self.cursor.execute(qry)
        return result

    def __exit__(self, type, value, trace_back):
        self.conn.close()
