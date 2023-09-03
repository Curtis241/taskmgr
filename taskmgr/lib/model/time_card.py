from taskmgr.lib.database.db_object import DatabaseObject
from taskmgr.lib.variables import CommonVariables


class TimeCard(DatabaseObject):
    """
    Contains the properties that are needed to represent a time card. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.vars = CommonVariables()
        self.__date = str()
        self.__date_timestamp = 0
        self.__time_in = 0
        self.__time_out = 0
        self.__elapsed_time = str()
        self.__total = str()
        self.__deleted = "False"

    @property
    def deleted(self) -> bool:
        return self.__deleted == "True"

    @deleted.setter
    def deleted(self, value: str):
        self.__deleted = str(value)

    @property
    def date(self):
        return self.__date
    
    @date.setter
    def date(self, date: str):
        if date is not None:
            self.__date = date

    @property
    def date_timestamp(self) -> int:
        return self.__date_timestamp
    
    @date_timestamp.setter
    def date_timestamp(self, value: int):
        self.__date_timestamp = int(value)
        
    @property
    def time_in(self) -> str:
        return str(self.__time_in)
    
    @time_in.setter
    def time_in(self, time_in: str):
        if time_in is not None:
            self.__time_in = time_in
    
    @property
    def time_out(self) -> str:
        return str(self.__time_out)
    
    @time_out.setter
    def time_out(self, time_out: str):
        if time_out is not None:
            self.__time_out = time_out

    @property
    def elapsed_time(self) -> str:
        return str(self.__elapsed_time)

    @elapsed_time.setter
    def elapsed_time(self, elapsed: str):
        if elapsed is not None:
            self.__elapsed_time = elapsed

    @property
    def total(self) -> str:
        return str(self.__total)

    @total.setter
    def total(self, total: str):
        if total is not None:
            self.__total = total

    def deserialize(self, obj_dict: dict):
        for key, value in obj_dict.items():
            if isinstance(key, str):
                setattr(self, key, value)
        return self

    def __eq__(self, other):
        return self.unique_id == other.unique_id

    def __iter__(self):
        yield 'index', self.index
        yield 'date', self.__date
        yield 'date_timestamp', self.__date_timestamp
        yield 'time_in', self.__time_in
        yield 'time_out', self.__time_out
        yield 'deleted', self.__deleted
        yield 'elapsed_time', self.__elapsed_time
        yield 'total', self.__total
        yield 'unique_id', self.unique_id
        yield 'last_updated', self.last_updated

