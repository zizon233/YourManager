import sys

sys.path.append("../")

from model.user import User

from client.sqlite3 import SQLITE3


def insert_new_message(time, user_id, room_id, message):
    with SQLITE3() as sqlite:
        sqlite.insert_new_message(time, user_id, room_id, message)


def get_all_message(room_id):
    with SQLITE3() as sqlite:
        messages = []
        raw_messages = sqlite.get_all_message(room_id)
        for raw_message in raw_messages:
            time, user_id, _, message = raw_message
            user = User(user_id)
            user.load()
            view_message = (time, user.user_name, message)
            messages.append(view_message)
            
        message_str = ""
        for message in messages:
            time, user_name, msg = message
            line = f"[{time}] {user_name} : {msg}\n"
            message_str += line
        return message_str


# offset으로 대화 불러오는 거
