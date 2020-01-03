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

    def get_object_list(self):
        if self.__db is not None:
            dict_list = self.__db.get()
            if len(dict_list) > 0:
                return self.__db.to_object_list(dict_list, self.__db_object)
            else:
                return []

    def clear_objects(self):
        self.__db.clear()

    # def save(self):
    #     """
    #     Gets objects (ie. Task, Snapshot) from local object list
    #     and converts to type dict and saves to database.
    #     :return: None
    #     """
    #     if self.__db is not None:
    #         self.__db.save(self.to_dict())

    # def retrieve(self):
    #     """
    #     Gets list of dicts representing objects and serializes
    #     to object using overridden from_dict method and stores
    #     in the local object list.
    #     :return:
    #     """
    #     if self.__db is not None:
    #         return self.__db.to_object_list(self.__db.get(), )

    # def to_dict(self):
    #     return [dict(obj) for obj in self.get_list()]

    # @abstractmethod
    # def from_dict(self, object_list):
    #     pass





    # def get_index(self):
    #     return len(self.__objects)

    # @staticmethod
    # def get_date_time_string() -> str:
    #     return Day(datetime.now()).to_date_time_string()
