import sys
import pymysql
import logging

sys.path.append("../")

import common

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(common.get_file_handler())


class MySQL:
    def __init__(self, host, user, password, db):
        self.host, self.user, self.password, self.db = (host, user, password, db)

    def __enter__(self):
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        return self

    def connect(self):
        conn = pymysql.connect(
            host=self.host, user=self.user, password=self.password, db=self.db
        )
        return conn

    def check_exist(self, table, column, value):
        qry = f"SELECT EXISTS (SELECT {column} \
            FROM {table} \
            WHERE {column} = %s limit 1) AS SUCCESS"
        self.cursor.execute(qry, value)
        result = self.cursor.fetchall()[0][0]
        return result

    def register_user(
        self, user_id, user_name, email, passwd_hash, salt, created_time, updated_time
    ):
        qry = f"INSERT INTO user (user_id, user_name, email, password, salt, created_time, updated_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(
            qry,
            (user_id, user_name, email, passwd_hash, salt, created_time, updated_time),
        )
        self.conn.commit()

    def get_password(self, user_id):
        qry = f"SELECT password \
            FROM user \
            WHERE user_id = %s"
        self.cursor.execute(qry, user_id)
        result = self.cursor.fetchall()[0][0]
        return result

    def get_salt(self, user_id):
        qry = f"SELECT salt \
            FROM user \
            WHERE user_id = %s"
        self.cursor.execute(qry, user_id)
        result = self.cursor.fetchall()[0][0]
        return result

    def get_user_info(self, user_id):
        qry = f"SELECT user_name, email \
            FROM user \
            WHERE user_id = %s"
        self.cursor.execute(qry, user_id)
        result = self.cursor.fetchall()[0]
        return result

    def __exit__(self, type, value, trace_back):
        self.conn.close()
