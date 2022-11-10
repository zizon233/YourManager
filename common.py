import json
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import secrets
from passlib.hash import pbkdf2_sha256

def get_server_info(db_kind):
    with open("./conf/conf.json") as conf:
        conf_file = json.load(conf)
        server_info = conf_file["server"][db_kind]
        return server_info

def get_file_handler():
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(process)d %(message)s"
    )

    file_handler = RotatingFileHandler(
        "./log/YourManager.log",
        maxBytes=256 * 1024 * 1024,
        backupCount=2,
    )
    file_handler.setFormatter(formatter)
    
    return file_handler

def make_hash(origin):
    salt = str(secrets.SystemRandom().getrandbits(128))
    hash = pbkdf2_sha256.hash(origin + salt)
    return hash, salt
    
def verify_hash(input, hash):
    return pbkdf2_sha256.verify(input, hash)