import calendar
import re
from copy import deepcopy
from typing import Callable, List
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import *
from taskmgr.lib.model.day import Day


from taskmgr.lib.variables import CommonVariables


class Today(Day):

    def __init__(self):
        super().__init__(datetime.now())


class Calendar:

    def __init__(self):
        self.weekday_list = range(0, 7)
        self.month_list = range(1, 13)
        self.weekday_abbrev_list = [{"key": 'su', "value": 6},
                                    {"key": 'm', "value": 0},
                                    {"key": 'tu', "value": 1},
                                    {"key": 'w', "value": 2},
                                    {"key": 'th', "value": 3},
                                    {"key": 'f', "value": 4},
                                    {"key": 'sa', "value": 5}]
        self.today = Today()
        self.vars = CommonVariables()

    @staticmethod
    def get_day_count_in_month(day: Day) -> int:
        return calendar.monthrange(day.year, day.month)[1]

    @staticmethod
    def get_week_count_in_month(month: int, year: int) -> int:
        return len(calendar.monthcalendar(year, month))

    @staticmethod
    def is_past(selected_day: Day, current_day: Day = Today()) -> bool:
        timedelta1 = selected_day.to_date_object() - current_day.to_date_object()
        if timedelta1.days < 0:
            return True
        return False

    @staticmethod
    def contains(day_list: List[Day], is_matched: Callable) -> bool:
        return len([day for day in day_list if is_matched(day)]) >= 1

    @staticmethod
    def contains_month(day_list: List[Day], selected_day=Today()) -> bool:
        return Calendar.contains(day_list, lambda day: day.month == selected_day.month)

    @staticmethod
    def contains_week(day_list: List[Day], selected_day=Today()) -> bool:
        return Calendar.contains(day_list, lambda day: day.week == selected_day.week)

    def get_weekday_number(self, day_abbrev: str) -> int:
        for obj in self.weekday_abbrev_list:
            if obj["key"] == str(day_abbrev).lower():
                return obj["value"]

    @staticmethod
    def get_closest_date(day_list: List[Day], current_day=None) -> Day:
        """
        Returns a future date string that is the closest to the current day
        :param day_list: list of Day objects
        :param current_day: Day object
        :return: Day object
        """
        if current_day is None:
            current_day = Today()

        diff_list = []
        # calculate the difference between current day and date string
        for day in day_list:
            timedelta1 = day.to_date_object() - current_day.to_date_object()
            diff_list.append(timedelta1.days)

        # return the date string using the smallest difference
        for index, diff_num in enumerate(diff_list):
            if diff_num >= 0:
                return day_list[index]

    @staticmethod
    def get_days(start_day, month_count: int = 1) -> List[Day]:
        """
        Gets all the days from today until the end of the month.

        :param month_count: number of months
        :param start_day: Day object
        :return: list of date string
        """
        assert type(start_day) is Day
        assert type(month_count) is int

        start = start_day.to_date_object()
        days = list(rrule(MONTHLY, count=month_count * 2, bymonthday=(-1, 1,), dtstart=start))
        return Calendar.fill(Day(days[0]), Day(days[-1]))

    @staticmethod
    def get_week_days(start_day: Day, weekday_number: int, month_count: int) -> List[Day]:
        """
        Returns all the days for the provided week day in a month.
        :param start_day: Day object
        :param weekday_number: integer (ie. 0-6) m=0 and su=6
        :param month_count: number of months
        :return: list of Days
        """
        assert type(start_day) is Day
        assert type(weekday_number) is int
        assert type(month_count) is int

        start = start_day.to_date_object()
        end = start + relativedelta(months=month_count)
        days = list(rrule(DAILY, wkst=MO, byweekday=weekday_number, dtstart=start, until=end))

        return [Day(dt) for dt in days]

    @staticmethod
    def get_work_week_days(start_day: Day, month_count: int) -> List[Day]:
        """
        Gets all days within a work week from today until the end of the month
        :param start_day: Day object
        :param month_count: number of months
        :return: list of date strings
        """
        assert type(start_day) is Day
        assert type(month_count) is int

        start = start_day.to_date_object()
        end = start + relativedelta(months=month_count)
        days = list(rrule(DAILY, wkst=MO, byweekday=(MO, TU, WE, TH, FR), dtstart=start, until=end))

        return [Day(dt) for dt in days]

    @staticmethod
    def get_day(today: Day, weekday_number: int) -> Day:
        """
        Gets the next calendar day in current week, next week, or next month that
        matches the provided weekday_number.
        :param today: Day object
        :param weekday_number: integer (ie. 0-6) m=0, su=6
        :return: Day object
        """
        assert type(today) is Day
        assert type(weekday_number) is int

        today = today.to_date_object()
        date_list = list(rrule(DAILY, count=1, wkst=MO, byweekday=weekday_number, dtstart=today))
        if date_list:
            return Day(date_list[0])

    def get_day_using_abbrev(self, day: Day, expression: str) -> Day:
        weekday_number = self.get_weekday_number(expression)
        return self.get_day(day, weekday_number)

    @staticmethod
    def get_first_day_in_month(day: Day) -> Day:
        day.day_number = 1
        return day

    def get_last_day_in_month(self, day: Day) -> Day:
        day.day_number = self.get_day_count_in_month(day)
        return day

    @staticmethod
    def get_first_day_in_week(day: Day) -> Day:
        return Day(day.to_date_object() - timedelta(days=day.weekday_number))

    @staticmethod
    def get_last_day_in_week(day: Day) -> Day:
        return Day(day.to_date_object() + timedelta(days=(6 - day.weekday_number)))

    @staticmethod
    def get_yesterday(day: Day) -> Day:
        return Day(day.to_date_object() - timedelta(days=1))

    @staticmethod
    def get_tomorrow(day: Day) -> Day:
        return Day(day.to_date_object() + timedelta(days=1))

    @staticmethod
    def fill(start_day: Day, end_day: Day) -> List[Day]:
        days = list(rrule(freq=DAILY, dtstart=start_day.to_date_object(), until=end_day.to_date_object()))
        return [Day(dt) for dt in days]

    def get_this_week(self, day: Day) -> List[Day]:
        return self.fill(self.get_first_day_in_week(deepcopy(day)), self.get_last_day_in_week(deepcopy(day)))

    def get_last_week(self, day: Day) -> List[Day]:
        past_day = Day(day.to_date_object() - timedelta(days=7))
        return self.fill(self.get_first_day_in_week(deepcopy(past_day)), self.get_last_day_in_week(deepcopy(past_day)))

    def get_next_week(self, day: Day) -> List[Day]:
        future_day = Day(day.to_date_object() + timedelta(days=7))
        return self.fill(self.get_first_day_in_week(deepcopy(future_day)), self.get_last_day_in_week(deepcopy(future_day)))

    def get_this_month(self, day: Day) -> List[Day]:
        return self.fill(self.get_first_day_in_month(deepcopy(day)), self.get_last_day_in_month(deepcopy(day)))

    def get_last_month(self, day: Day) -> List[Day]:
        first_day = self.get_first_day_in_month(day)
        past_day = Day(first_day.to_date_object() - timedelta(days=1))
        return self.fill(self.get_first_day_in_month(deepcopy(past_day)), past_day)

    def get_next_month(self, day: Day) -> List[Day]:
        last_day = self.get_last_day_in_month(day)
        future_day = Day(last_day.to_date_object() + timedelta(days=1))
        return self.fill(future_day, self.get_last_day_in_month(deepcopy(future_day)))

    @staticmethod
    def is_short_date(expression: str) -> bool:
        if re.match('^[a-z]{3} \d{1,2}$', str(expression).lower()) is not None:
            month, day_number = str(expression).split()
            if 31 >= int(day_number) >= 1:
                return True
        return False

    @staticmethod
    def is_valid(expression: str) -> bool:
        try:
            parse(expression)
            return True
        except ParserError:
            return False

    @staticmethod
    def parse_date_time(expression: str) -> Day:
        return Day(parse(expression))

    def parse_recurring_abbrev(self, day: Day, expression: str, month_count: int) -> List[Day]:
        prefix, abbrev = str(expression).split()
        weekday_number = self.get_weekday_number(abbrev)
        return self.get_week_days(day, weekday_number, month_count)

