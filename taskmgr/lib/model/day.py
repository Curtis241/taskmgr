import calendar
from datetime import datetime

from taskmgr.lib.variables import CommonVariables


class Day:
    def __init__(self, dt):
        assert type(dt) is datetime
        self.dt = dt
        self.day_number = dt.day
        self.month = dt.month
        self.year = dt.year
        self.timestamp = dt.timestamp()
        self.weekday_number = dt.weekday()
        self.week = self.get_week(self.day_number, self.weekday_number, self.month, self.year)
        self.vars = CommonVariables()

    def to_timestamp(self):
        return int(self.dt.timestamp())

    def to_date_list(self):
        return [self.to_date_string()]

    def to_date_expression(self):
        return f"{self.month} {self.day_number}"

    def to_date_string(self):
        month = Day.pad(self.month)
        day = Day.pad(self.day_number)
        return f"{self.year}-{month}-{day}"

    def to_date_time_string(self):
        return datetime.strftime(self.dt, self.vars.date_time_format)

    def to_date_time(self):
        month = self.pad(self.month)
        day = self.pad(self.day_number)
        return datetime.strptime(f"{self.year}-{month}-{day}", self.vars.date_format)

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

