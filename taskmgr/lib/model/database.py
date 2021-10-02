import json
import os
import uuid
from abc import ABC, abstractmethod
from copy import copy
from datetime import datetime
from typing import List

import redis
import ujson

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class DatabaseObject(ABC):

    def __init__(self, object_name):
        self.__unique_id = None
        self.__index = 0
        self.__last_updated = str()
        self.__object_name = object_name

    @property
    def unique_id(self):
        return self.__unique_id

    @unique_id.setter
    def unique_id(self, unique_id):
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
    def last_updated(self, last_updated):
        self.__last_updated = last_updated

    @abstractmethod
    def deserialize(self, obj_dict): pass

    @abstractmethod
    def get_redis_db_id(self): pass


class GenericDatabase(ABC):
    """Generic base class to support Yaml, Json file databases and redis."""
    logger = AppLogger("database").get_logger()

    def __init__(self):
        self.resources_dir = CommonVariables().resources_dir

    @abstractmethod
    def initialize(self, obj):
        """
        Executes initialization activities such as constructing the file name if it is a
        file database or selects the logical redis database
        :param obj: Object that subclasses DatabaseObject
        :return: None
        """
        pass

    @abstractmethod
    def replace(self, obj):
        """
        Replaces specific object using obj.index.
        :param index: integer
        :param obj: Object that subclasses DatabaseObject
        :return: obj
        """
        pass

    @abstractmethod
    def append(self, obj):
        """
        Adds the object to end of the list of objects and assigns a new index id based
        on the number of existing objects. Objects are preserved using a soft delete method.
        Only the deleted parameter is changed from False to True. The index id is unique
        and should not be re-used.
        :param obj:
        :return: obj
        """
        pass

    @abstractmethod
    def set(self, obj_list):
        """
        Acts on objects in a list. It replaces an object when the index matches OR adds to the end
        of the list when the index does not match an existing one.
        :param obj_list:
        :return:
        """
        pass

    @abstractmethod
    def get(self) -> List[dict]:
        """
        Converts a stored database object (ie. json object) to a python dictionary. Use the to_object_list
        method to convert the dictionary to an object that implements the DatabaseObject class.
        :return:
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def clear(self):
        pass

    @staticmethod
    def contains_dict(dict_list) -> bool:
        if dict_list is not None:
            assert type(dict_list) is list
            if len(dict_list) >= 1:
                assert type(dict_list[0]) is dict
                return True
        return False

    @staticmethod
    def contains_database_object(obj_list) -> bool:
        if obj_list is not None:
            assert type(obj_list) is list
            if len(obj_list) >= 1:
                if isinstance(obj_list[0], DatabaseObject):
                    return True
                else:
                    raise ValueError("Provided obj must subclass DatabaseObject")
        return False

    @staticmethod
    def to_object_list(dict_list, obj) -> List:
        if dict_list is not None:
            assert isinstance(obj, DatabaseObject)
            assert GenericDatabase.contains_dict(dict_list)

            obj_list = list()
            for obj_dict in dict_list:
                obj = copy(obj)
                obj = obj.deserialize(obj_dict)
                obj_list.append(obj)
            return obj_list
        else:
            return []

    @staticmethod
    def to_dict_list(obj_list) -> List:
        if obj_list is not None:
            assert GenericDatabase.contains_database_object(obj_list)
            try:
                return [dict(obj) for obj in obj_list]
            except TypeError as ex:
                GenericDatabase.logger.error(f"{ex}. Provided obj must contain __iter__ method")
                raise ex
        return []

    @staticmethod
    def to_json(obj):
        assert isinstance(obj, DatabaseObject)
        try:
            return json.dumps(dict(obj))
        except TypeError as ex:
            GenericDatabase.logger.error(f"{ex}. Provided obj must contain __iter__ method")
            raise ex

    @staticmethod
    def get_last_updated() -> str:
        return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    def get_file_path(self, obj, file_ext) -> str:
        assert isinstance(obj, DatabaseObject)
        path = f"{self.resources_dir}{str(obj.object_name).lower()}_db.{file_ext}"
        if not self.file_exists(path):
            os.makedirs(self.resources_dir, 0o777, exist_ok=True)
        return path

    @staticmethod
    def file_exists(path) -> bool:
        return os.path.exists(path)

    def remove_file(self, path):
        try:
            if self.file_exists(path):
                os.remove(path)
        except FileNotFoundError as ex:
            self.logger.error(f"Cannot remove database file {ex}")
            raise

    @staticmethod
    def get_list_index(obj, dict_list):
        assert type(dict_list) is list
        assert isinstance(obj, DatabaseObject)
        index_list = [index for index, obj_dict in enumerate(dict_list, start=0) if obj_dict["index"] == obj.index]
        if len(index_list) == 1:
            return index_list[0]

    @staticmethod
    def set_unique_id(obj) -> DatabaseObject:
        """
        A unique id should only be assigned once when the object is appended or replaced.
        :param obj: Object that subclasses DatabaseObject
        :return:
        """
        assert isinstance(obj, DatabaseObject)
        if obj.unique_id is None:
            obj.unique_id = uuid.uuid4().hex
        return obj

    @staticmethod
    def get_last_index(dict_list) -> int:
        if dict_list is not None:
            count = len(dict_list)
            if count > 0:
                return count + 1
            else:
                return 1


class JsonFileDatabase(GenericDatabase):
    """
    Manages saving and retrieving tasks as dict object to a json file
    located in the resource directory.
    """

    logger = AppLogger("json_file_database").get_logger()

    def __init__(self):
        super().__init__()
        self.path = None

    def initialize(self, obj):
        """
        Constructs the db file path
        :param obj: Class object that implements DatabaseObject
        :return: None
        """
        self.path = self.get_file_path(obj, "json")

    def replace(self, obj):
        assert isinstance(obj, DatabaseObject)
        assert obj.index > 0

        dict_list = self.get()
        if dict_list is not None:
            index = self.get_list_index(obj, dict_list)
            if index is not None:
                obj = self.set_unique_id(obj)
                obj.last_updated = self.get_last_updated()
                dict_list[index] = dict(obj)
                self.save(dict_list)

    def append(self, obj):
        assert isinstance(obj, DatabaseObject)

        dict_list = self.get()
        if dict_list is not None:
            obj.index = self.get_last_index(dict_list)
            obj = self.set_unique_id(obj)
            obj.last_updated = self.get_last_updated()
            dict_list.append(dict(obj))
            self.save(dict_list)
        else:
            obj.index = 1
            obj = self.set_unique_id(obj)
            obj.last_updated = self.get_last_updated()
            self.save([dict(obj)])

    def save(self, dict_list):
        with open(self.path, 'w') as outfile:
            self.logger.debug("Saved json database")
            ujson.dump(dict_list, outfile)

    def set(self, obj_list):
        self.save(self.to_dict_list(obj_list))

    def get(self) -> List[dict]:
        if self.exists():
            self.logger.debug("Retrieved json database")
            with open(self.path, 'r') as infile:
                return ujson.load(infile)
        return []

    def exists(self) -> bool:
        return self.file_exists(self.path)

    def clear(self):
        if self.exists():
            self.remove_file(self.path)


class RedisDatabase(GenericDatabase):
    """
    Manages saving and retrieving objects to a redis database. Retrieve method should be called
    before save to maintain a consistent state.
    """

    logger = AppLogger("redis_database").get_logger()

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.db = None

    def build_db_list(self):
        # Max number of keys in a redis logical databases is 16. Scan all
        # logical databases to identify what object belongs in each.
        db_list = []
        for index in range(0, 16):
            db = redis.Redis(host=self.host, port=self.port, db=index)
            keys = db.keys("1:*")
            if len(keys) == 1:
                key = str(keys[0].decode("utf-8")).lstrip("1:")
                db_list.append((db, key))
            else:
                db_list.append((db, None))
        return db_list

    def initialize(self, obj, test_mode=False):
        """
        Retrieves the redis db id from the object so it can be saved or updated.
        :param obj: Object that subclasses DatabaseObject
        :param test_mode: Unsupported
        :return: None
        """
        self.db = redis.Redis(host=self.host, port=self.port, db=obj.get_redis_db_id())

    @staticmethod
    def __key(obj):
        return f"{obj.index}:{obj.object_name}"

    def replace(self, obj):
        assert isinstance(obj, DatabaseObject)
        assert obj.index > 0
        self.set([obj])

    def append(self, obj):
        assert isinstance(obj, DatabaseObject)
        self.set([obj])

    def set(self, obj_list):
        """
        Updates or inserts new objects that inherit from DatabaseObject. When key matches existing key an update
        occurs, but if there is no match then a new key is created.
        :param obj_list: List containing class objects
        :return: None
        """
        assert self.contains_database_object(obj_list)
        if self.exists():
            for obj in obj_list:
                if not self.db.exists(self.__key(obj)):
                    obj.index = self.get_last_index(self.db.keys())

                obj = self.set_unique_id(obj)
                obj.last_updated = self.get_last_updated()
                self.db.hset(self.__key(obj), "last_updated", obj.last_updated)
                self.db.hset(self.__key(obj), "data", self.to_json(obj))

    def get(self) -> List[dict]:
        if self.db is not None:
            return [json.loads(self.db.hget(key, "data")) for key in sorted(self.db.keys())]
        else:
            return []

    def exists(self):
        db = redis.Redis(host=self.host, port=self.port, db=0)
        return db.ping()

    def clear(self):
        for db_item in self.build_db_list():
            for key in db_item[0].keys():
                db_item[0].delete(key)
