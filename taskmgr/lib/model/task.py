from taskmgr.lib.database.object import DatabaseObject
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.variables import CommonVariables


class Task(DatabaseObject):
    """
    Contains the properties that are needed to represent a task. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """

    def __init__(self, name: str = "default"):
        super().__init__(self.__class__.__name__)
        self.vars = CommonVariables()
        self.__name = name
        self.__label = self.vars.default_label
        self.__time_spent = 0
        self.__project = self.vars.default_project_name
        self.__due_date = Today().to_date_string()
        self.__due_date_timestamp = Today().to_timestamp()
        self.__completed = 0
        self.__deleted = 0

    @property
    def due_date(self) -> str:
        return self.__due_date

    @due_date.setter
    def due_date(self, due_date: str):
        if due_date is not None:
            self.__due_date = self.to_str(due_date)

    @property
    def due_date_timestamp(self) -> int:
        return self.__due_date_timestamp

    @due_date_timestamp.setter
    def due_date_timestamp(self, value: int):
        self.__due_date_timestamp = value

    @property
    def completed(self) -> bool:
        return bool(self.__completed)

    @completed.setter
    def completed(self, value: bool):
        self.__completed = int(value)

    @property
    def deleted(self) -> bool:
        return bool(self.__deleted)

    @deleted.setter
    def deleted(self, value: bool):
        self.__deleted = int(value)

    @property
    def project(self) -> str:
        return self.__project

    @project.setter
    def project(self, value: str):
        if value is not None:
            self.__project = self.to_str(value)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if value is not None:
            self.__name = self.to_str(value)

    @property
    def label(self) -> str:
        return self.__label

    @label.setter
    def label(self, value: str):
        if value is not None:
            self.__label = self.to_str(value)

    @property
    def time_spent(self) -> float:
        return self.__time_spent

    @time_spent.setter
    def time_spent(self, value: float):
        if value is not None:
            self.__time_spent = float(value)

    def deserialize(self, obj_dict: dict):
        for key, value in obj_dict.items():
            setattr(self, str(key, 'utf-8'), value)
        return self

    def __eq__(self, other):
        existing = (self.unique_id, self.__name, self.__label, self.__project)
        new = (other.unique_id, other.name, other.label, other.project)
        return existing == new

    def __iter__(self):
        yield 'index', self.index
        yield 'name', self.__name
        yield 'label', self.__label
        yield 'deleted', self.__deleted
        yield 'time_spent', self.__time_spent
        yield 'project', self.__project
        yield 'due_date', self.__due_date
        yield 'due_date_timestamp', self.__due_date_timestamp
        yield 'completed', self.__completed
        yield 'unique_id', self.unique_id
        yield 'last_updated', self.last_updated




