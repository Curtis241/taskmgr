from abc import ABC, abstractmethod


class DatabaseObject(ABC):

    def __init__(self, object_name):
        self.__unique_id = None
        self.__index = 0
        self.__last_updated = str()
        self.__object_name = object_name

    @staticmethod
    def to_bool(value: str) -> bool:
        if value in ['True', 'False']:
            return eval(value)
        else:
            return bool(value)

    @property
    def unique_id(self):
        return self.__unique_id

    @unique_id.setter
    def unique_id(self, unique_id: str):
        if self.__unique_id is None:
            self.__unique_id = unique_id

    @property
    def object_name(self):
        return self.__object_name

    @object_name.setter
    def object_name(self, object_name):
        self.__object_name = object_name

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        self.__index = int(index)

    @property
    def last_updated(self):
        return self.__last_updated

    @last_updated.setter
    def last_updated(self, last_updated: str):
        self.__last_updated = last_updated

    @abstractmethod
    def deserialize(self, obj_dict): pass

    @abstractmethod
    def __iter__(self): pass
