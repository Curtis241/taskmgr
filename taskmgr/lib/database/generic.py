import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.database.object import DatabaseObject
from taskmgr.lib.variables import CommonVariables


class GenericDatabase(ABC):
    """Generic base class to support redis databases."""
    logger = AppLogger("generic_database").get_logger()

    def __init__(self):
        self.resources_dir = CommonVariables().resources_dir

    @abstractmethod
    def replace_object(self, index: int, obj: DatabaseObject) -> DatabaseObject:
        """
        Replaces specific object using obj.index.
        :param index: Existing task index
        :param obj: Object that subclasses DatabaseObject
        :return: obj
        """
        pass

    @abstractmethod
    def append_object(self, obj: DatabaseObject) -> DatabaseObject:
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
    def get_object_list(self) -> List[dict]:
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
    def contains_database_object(obj_list: list) -> bool:
        if obj_list is not None:
            assert type(obj_list) is list
            if len(obj_list) >= 1:
                if isinstance(obj_list[0], DatabaseObject):
                    return True
                else:
                    raise ValueError("Provided obj must subclass DatabaseObject")
        return False

    @staticmethod
    def get_last_updated() -> str:
        return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_unique_id() -> str:
        """
        A unique id should only be assigned once when the object is appended or replaced.
        :return: unique id string
        """
        return uuid.uuid4().hex

    @staticmethod
    def get_last_index(dict_list: list) -> int:
        if dict_list is not None:
            count = len(dict_list)
            if count > 0:
                return count + 1
            else:
                return 1
