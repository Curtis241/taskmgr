from datetime import datetime

from taskmgr.lib.variables import CommonVariables


class DueDate(object):
    """The DueDate object was created to support reoccurring tasks.
    When there are many dates each date can be marked as completed."""

    def __init__(self, date_string=""):
        self.__completed = False
        self.__date_string = date_string
        self.vars = CommonVariables()

    def is_empty(self) -> bool:
        return len(self.__date_string) == 0

    def to_date_time(self) -> datetime:
        return datetime.strptime(self.date_string, self.vars.date_format)

    @property
    def completed(self) -> bool:
        return self.__completed

    @completed.setter
    def completed(self, is_completed: bool):
        assert type(is_completed) is bool
        self.__completed = is_completed

    @property
    def date_string(self) -> str:
        return self.__date_string

    @date_string.setter
    def date_string(self, date_string: str):
        """
        Store a datetime object converted to a date string using a formatter.
        See the CommonVariables.date_format formatter
        :param date_string:
        :return:
        """
        assert type(date_string) is str
        self.__date_string = date_string

    def to_dict(self) -> dict:
        """
        Converts object to dict
        :return:  dict
        """
        return {"date_string": self.__date_string, "completed": self.__completed}

    def from_dict(self, due_date: dict):
        """
        Converts dict to object
        :param due_date: DueDate dict
        :return: DueDate object
        """
        if "date_string" in due_date:
            self.__date_string = due_date["date_string"]

        if "completed" in due_date:
            self.__completed = due_date["completed"]
        return self

    def __eq__(self, other):
        return (self.__date_string, self.__completed) == (other.date_string, other.completed)

