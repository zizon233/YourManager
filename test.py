from model.user import User
from base64 import b64encode, b64decode
import json
from client.mysql import MySQL
import common
from passlib.hash import pbkdf2_sha256

user = User("test", "test")

print(user.__repr__)

byte = b"test"

print(byte)

byte = b64encode(byte)

print(byte)

byte = byte.decode("utf-8")

print(byte)

data = json.dumps({"test": byte})

print(data)

print(b64decode(byte.encode("utf-8")))

mysql_info = common.get_server_info("mysql")
print(mysql_info)
with MySQL(
    mysql_info["host"], mysql_info["user"], mysql_info["password"], "YourManager"
) as mysql:
    print("connect.")

print(common.get_file_handler())

test_pass = pbkdf2_sha256.hash("rhtn0195!")

print(
    pbkdf2_sha256.verify(
        "rhtn0195!",
        test_pass,
    )
)
