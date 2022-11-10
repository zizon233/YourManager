from logging import setLogRecordFactory


class Room:
    def __init__(
        self,
        room_id,
        room_name=None,
        passwd_hash=None,
        salt=None,
    ):
        self.__room_id = room_id
        self.__room_name = room_name
        self.__passwd_hash = passwd_hash
        self.__salt = salt

    @property
    def room_id(self):
        return self.__room_id

    @room_id.setter
    def room_id(self, room_id):
        self.__room_id = room_id

    @property
    def room_name(self):
        return self.__room_name

    @room_name.setter
    def room_name(self, room_name):
        self.__room_name = room_name
        
    @property
    def passwd_hash(self):
        return self.__passwd_hash

    @passwd_hash.setter
    def passwd_hash(self, passwd_hash):
        self.__passwd_hash = passwd_hash
        
    @property
    def salt(self):
        return self.__salt

    @room_id.setter
    def salt(self, salt):
        self.__salt = salt