from abc import abstractmethod
from datetime import datetime

from taskmgr.lib.presenter.date_generator import Day


class Model:

    def __init__(self, file_database):
        self.__db = file_database
        self.__objects = list()
        self.retrieve()

    def insert(self, index, obj):
        self.__objects[index] = obj

    def append(self, obj):
        self.__objects.append(obj)

    def save(self):
        if self.__db is not None:
            self.__db.save(self.to_dict())

    def retrieve(self):
        if self.__db is not None:
            objects_list = self.__db.retrieve()
            if objects_list is not None:
                self.__objects = list()
                self.__objects = self.from_dict(objects_list)

    def to_dict(self):
        return [dict(obj) for obj in self.get_list()]

    @abstractmethod
    def from_dict(self, object_list): pass

    @abstractmethod
    def add(self, obj): pass

    def get_list(self):
        return self.__objects

    def clear(self):
        self.__objects = []

    def get_index(self):
        return len(self.__objects)

    @staticmethod
    def get_date_time_string() -> str:
        return Day(datetime.now()).to_date_time_string()


