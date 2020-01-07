from typing import List

from taskmgr.lib.model.database import GenericDatabase, DatabaseObject


class Model:
    """
    Provides a facade between the classes that implement Model and the database.
    """

    def __init__(self, db, db_object):
        assert isinstance(db, GenericDatabase)
        assert isinstance(db_object, DatabaseObject)
        self.__db = db
        self.__db_object = db_object

    def replace_object(self, index, obj):
        obj.index = index
        return self.__db.replace(obj)

    def append_object(self, obj):
        return self.__db.append(obj)

    def update_objects(self, obj_list):
        return self.__db.set(obj_list)

    def get_object_list(self) -> List:
        if self.__db is not None:
            dict_list = self.__db.get()
            if dict_list is not None and len(dict_list) > 0:
                return self.__db.to_object_list(dict_list, self.__db_object)
        return []

    def clear_objects(self):
        self.__db.clear()

