import calendar
from datetime import datetime

from taskmgr.lib.variables import CommonVariables


class Day:
    def __init__(self, dt: datetime):
        assert type(dt) is datetime
        self.__dt = dt
        self.day_number = dt.day
        self.month = dt.month
        self.year = dt.year
        self.timestamp = int(dt.timestamp())
        self.weekday_number = dt.weekday()
        self.week = self.get_week(self.day_number, self.weekday_number, self.month, self.year)
        self.vars = CommonVariables()


    def to_datetime(self):
        return self.__dt

    def to_timestamp(self):
        """
        Returns the timestamp as integer from the internal datetime object
        """
        return int(self.timestamp)

    def to_date_list(self):
        """
        Provides list of date strings in format YYYY-MM-DD
        """
        return [self.to_date_string()]

    def to_date_string(self):
        """
        Creates single date string in the format YYYY-MM-DD
        """
        month = self.pad(self.month)
        day = self.pad(self.day_number)
        return f"{self.year}-{month}-{day}"

    def to_date_object(self):
        """
        Returns datetime object for YYYY-MM-DD
        """
        return datetime.strptime(self.to_date_string(), self.vars.date_format)

    def to_date_timestamp(self):
        """
        Provides timestamp representing YYYY-MM-DD only.
        """
        return int(self.to_date_object().timestamp())

    def to_date_time_string(self):
        """
        Gets string in format YYYY-MM-DD HH:MM:SS
        """
        return datetime.strftime(self.__dt, self.vars.date_time_format)

    @staticmethod
    def pad(value):
        if len(str(value)) == 1:
            return "{0:0=2d}".format(value)
        return str(value)

    @staticmethod
    def get_week(day, weekday_number, month, year):
        cal = calendar.Calendar()
        for week_count, week_list in enumerate(cal.monthdays2calendar(year, month), start=1):
            for day_tuple in week_list:
                if day_tuple == (day, weekday_number):
                    return week_count

