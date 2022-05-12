from taskmgr.lib.database.object import DatabaseObject


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
        self.__total_time = 0
        self.__average_time = 0
        self.__due_date = str()

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
    def count(self, value):
        self.__count = value

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, value):
        self.__completed = value

    @property
    def incomplete(self):
        return self.__incomplete

    @incomplete.setter
    def incomplete(self, value):
        self.__incomplete = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    @property
    def total_time(self):
        return self.__total_time

    @total_time.setter
    def total_time(self, value):
        self.__total_time = value

    @property
    def average_time(self):
        return self.__average_time

    @average_time.setter
    def average_time(self, value):
        self.__average_time = value

    def deserialize(self, obj_dict):
        for key, value in obj_dict.items():
            setattr(self, key, value)
        return self

    def compose_summary(self):
        return {"count": self.__count,
                "completed": self.__completed,
                "incomplete": self.__incomplete,
                "deleted": self.__deleted,
                "average_time": self.__average_time,
                "total_time": self.__total_time}

    def __iter__(self):
        yield 'index', self.index
        yield 'due_date', self.due_date
        yield 'count', self.__count
        yield 'completed', self.__completed
        yield 'incomplete', self.__incomplete
        yield 'deleted', self.__deleted
        yield 'average_time', self.__average_time
        yield 'total_time', self.__total_time
