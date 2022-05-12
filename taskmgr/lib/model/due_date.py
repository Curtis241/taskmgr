from datetime import datetime

from taskmgr.lib.variables import CommonVariables


class DueDate:
    """The DueDate object"""

    def __init__(self, date_string: str):
        assert type(date_string) is str
        assert len(date_string) > 0, "Date string is empty"

        self.__date_string = date_string
        self.vars = CommonVariables()

    def to_date_time(self) -> datetime:
        return datetime.strptime(self.__date_string, self.vars.date_format)

    def to_timestamp(self) -> int:
        return int(self.to_date_time().timestamp())

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

    def __eq__(self, other):
        return self.__date_string == other

