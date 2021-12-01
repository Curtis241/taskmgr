from taskmgr.lib.model.database import DatabaseObject


class Snapshot(DatabaseObject):
    """
    Contains properties needed to define a data Snapshot. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.__count = 0
        self.__completed = 0
        self.__incomplete = 0
        self.__deleted = 0
        self.__due_date = str()

    def get_redis_db_id(self):
        return 1

    @property
    def due_date(self):
        return self.__due_date

    @due_date.setter
    def due_date(self, due_date):
        self.__due_date = due_date

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, count):
        self.__count = count

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, completed):
        self.__completed = completed

    @property
    def incomplete(self):
        return self.__incomplete

    @incomplete.setter
    def incomplete(self, incomplete):
        self.__incomplete = incomplete

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, deleted):
        self.__deleted = deleted

    @property
    def entity_kind(self):
        return self.__class__.__name__

    def deserialize(self, obj_dict):
        for key, value in obj_dict.items():
            setattr(self, key, value)
        return self

    def compose_summary(self):
        return {"count": self.__count,
                "completed": self.__completed,
                "incomplete": self.__incomplete,
                "deleted": self.__deleted}

    def __iter__(self):
        yield 'index', self.index
        yield 'due_date', self.due_date
        yield 'count', self.__count
        yield 'completed', self.__completed
        yield 'incomplete', self.__incomplete
        yield 'deleted', self.__deleted
