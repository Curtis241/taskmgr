from taskmgr.lib.database.db_object import DatabaseObject


class Snapshot(DatabaseObject):
    """
    Contains properties needed to define a data Snapshot. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """

    def __init__(self, is_summary=False):
        super().__init__(self.__class__.__name__)
        self.__task_count = 0
        self.__complete_count = 0
        self.__incomplete_count = 0
        self.__delete_count = 0
        self.__total_time = 0
        self.__average_time = 0
        self.__due_date = str()
        self.__due_date_timestamp = 0
        self.__is_summary = is_summary

    @property
    def is_summary(self):
        return self.__is_summary

    @property
    def due_date(self):
        return self.__due_date

    @due_date.setter
    def due_date(self, due_date):
        self.__due_date = due_date

    @property
    def due_date_timestamp(self) -> int:
        return self.__due_date_timestamp

    @due_date_timestamp.setter
    def due_date_timestamp(self, value: int):
        self.__due_date_timestamp = int(value)

    @property
    def task_count(self):
        return self.__task_count

    @task_count.setter
    def task_count(self, value):
        self.__task_count = int(value)

    @property
    def complete_count(self):
        return self.__complete_count

    @complete_count.setter
    def complete_count(self, value):
        self.__complete_count = int(value)

    @property
    def incomplete_count(self):
        return self.__incomplete_count

    @incomplete_count.setter
    def incomplete_count(self, value):
        self.__incomplete_count = int(value)

    @property
    def delete_count(self):
        return self.__delete_count

    @delete_count.setter
    def delete_count(self, value):
        self.__delete_count = int(value)

    @property
    def total_time(self):
        return self.__total_time

    @total_time.setter
    def total_time(self, value):
        self.__total_time = float(value)

    @property
    def average_time(self):
        return self.__average_time

    @average_time.setter
    def average_time(self, value):
        self.__average_time = float(value)

    def deserialize(self, obj_dict):
        for key, value in obj_dict.items():
            setattr(self, key, value)
        return self

    def compose_summary(self):
        return {"task_count": self.__task_count,
                "complete_count": self.__complete_count,
                "incomplete_count": self.__incomplete_count,
                "delete_count": self.__delete_count,
                "average_time": self.__average_time,
                "total_time": self.__total_time}

    def update(self, snapshot):
        self.__task_count = snapshot.task_count
        self.__complete_count = snapshot.complete_count
        self.__incomplete_count = snapshot.incomplete_count
        self.__delete_count = snapshot.delete_count
        self.__average_time = snapshot.average_time
        self.__total_time = snapshot.total_time

    def __iter__(self):
        yield 'index', self.index
        yield 'unique_id', self.unique_id
        yield 'due_date', self.due_date
        yield 'due_date_timestamp', self.__due_date_timestamp
        yield 'task_count', self.__task_count
        yield 'complete_count', self.__complete_count
        yield 'incomplete_count', self.__incomplete_count
        yield 'delete_count', self.__delete_count
        yield 'average_time', self.__average_time
        yield 'total_time', self.__total_time
