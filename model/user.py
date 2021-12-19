import sys
import datetime
from pytz import timezone

sys.path.append("../")

import common

from client.mysql import MySQL


class User:
    def __init__(
        self,
        user_id,
        user_name=None,
        passwd_hash=None,
        salt=None,
        email=None,
        authenticated=False,
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.passwd_hash = passwd_hash
        self.email = email
        self.salt = salt
        self.authenticated = authenticated

    def __repr__(self):
        r = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "passwd_hash": self.passwd_hash,
            "email": self.email,
            "authenticated": self.authenticated,
        }
        return str(r)

    def can_login(self, passwd_hash):
        return self.passwd_hash == passwd_hash

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def register(self):
        mysql_info = common.get_server_info("mysql")
        with MySQL(
            mysql_info["host"],
            mysql_info["user"],
            mysql_info["password"],
            "YourManager",
        ) as mysql:
            current_time = datetime.datetime.now(timezone("Asia/Seoul"))
            mysql.register_user(
                self.user_id,
                self.user_name,
                self.email,
                self.passwd_hash,
                self.salt,
                current_time,
                current_time,
            )

    def check_user_exist(self):
        mysql_info = common.get_server_info("mysql")
        with MySQL(
            mysql_info["host"],
            mysql_info["user"],
            mysql_info["password"],
            "YourManager",
        ) as mysql:
            if mysql.check_exist("user", "user_id", self.user_id):
                return True
            return False

    def load(self):
        mysql_info = common.get_server_info("mysql")
        with MySQL(
            mysql_info["host"],
            mysql_info["user"],
            mysql_info["password"],
            "YourManager",
        ) as mysql:
            self.user_name, self.email = mysql.get_user_info(self.user_id)

    @staticmethod
    def get_passwd_hash(user_id):
        mysql_info = common.get_server_info("mysql")
        with MySQL(
            mysql_info["host"],
            mysql_info["user"],
            mysql_info["password"],
            "YourManager",
        ) as mysql:
            password = mysql.get_password(user_id)
        return password

    @staticmethod
    def get_salt(user_id):
        mysql_info = common.get_server_info("mysql")
        with MySQL(
            mysql_info["host"],
            mysql_info["user"],
            mysql_info["password"],
            "YourManager",
        ) as mysql:
            password = mysql.get_salt(user_id)
        return password
