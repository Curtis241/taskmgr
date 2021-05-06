import calendar
from typing import Callable, List
from datetime import datetime, timedelta
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.due_date import DueDate

from taskmgr.lib.variables import CommonVariables


class Today(Day):

    def __init__(self):
        super().__init__(datetime.now())


class Calendar:

    def __init__(self):
        self.weekday_list = range(0, 7)
        self.month_list = range(1, 13)
        self.weekdays_list = [('su', 6), ('m', 0), ('tu', 1), ('w', 2), ('th', 3), ('f', 4), ('sa', 5)]
        self.today = Today()
        self.vars = CommonVariables()

    @staticmethod
    def __exists(day: tuple, dates: list):
        for date in dates:
            if date[0] == day[0]:
                return True
        return False

    def __add(self, day, date_list):
        day_tuple = (day.to_date_string(), day)
        if not self.__exists(day_tuple, date_list):
            date_list.append(day_tuple)
        return date_list

    @staticmethod
    def is_past(due_date: DueDate, current_day=Today()) -> bool:
        timedelta1 = due_date.to_date_time() - current_day.to_date_time()
        if timedelta1.days < 0:
            return True
        return False

    @staticmethod
    def contains(due_dates: List[DueDate], is_matched: Callable) -> bool:
        return len([due_date for due_date in due_dates if is_matched(due_date)]) >= 1

    @staticmethod
    def contains_month(due_dates: List[DueDate], selected_day=Today()) -> bool:
        return Calendar.contains(due_dates, lambda due_date: Day(due_date.to_date_time()).month == selected_day.month)

    @staticmethod
    def contains_week(due_dates: List[DueDate], selected_day=Today()) -> bool:
        return Calendar.contains(due_dates, lambda due_date: Day(due_date.to_date_time()).week == selected_day.week)

    def get_closest_due_date(self, due_dates: List[DueDate], current_day=None):
        """
        Returns a future date string that is the closest to the current day
        :param due_dates: list of due_date objects with the format yyyy-mm-dd
        :param current_day: Day object
        :return:
        Date string
        """
        if current_day is None:
            current_day = Today()

        diff_list = []
        # calculate the difference between current day and date string
        for due_date in due_dates:
            if len(due_date.date_string) > 0:
                day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))
                timedelta1 = day.to_date_time() - current_day.to_date_time()
                diff_list.append(timedelta1.days)

        # return the date string using the smallest difference
        for index, diff_num in enumerate(diff_list):
            if diff_num >= 0:
                return due_dates[index]

        return None

    def get_weekday_number(self, day_abbrev):
        day_tuple = [e[1] for e in self.weekdays_list if day_abbrev == e[0]]
        if len(day_tuple) == 0:
            return None
        else:
            return day_tuple[0]

    def get_year(self, year):
        date_list = list()
        for year_list in calendar.Calendar().yeardatescalendar(year):
            for month_list in year_list:
                for week_number, week_list in enumerate(month_list, start=1):
                    for date in week_list:
                        day = Day(datetime(year=date.year, month=date.month, day=date.day))
                        if day.year == year:
                            date_list = self.__add(day, date_list)
        return date_list

    @staticmethod
    def compose_search_list(start_day, month_count):
        """
        Creates a list containing month and year for current year and next year to filter the list
        returned by get_year()
        :param start_day:  Day object
        :param month_count: number of months
        :return:
        [[1, 2019], [2, 2019], [3, 2019]]
        """
        search_list = list()
        search_list.append([start_day.month, start_day.year])

        for i in range(1, month_count):
            month = start_day.month + i
            search_list.append([month, start_day.year])

        if (start_day.month + month_count) > 12:
            for t in search_list:
                if t[0] > 12:
                    t[0] = (t[0] - 12)
                    t[1] = (t[1] + 1)
        return search_list

    def get_month_range(self, start_day, month_count):
        """
        Retrieves a list of months from the current month for the provided number of months.
        :param start_day: Day object
        :param month_count: number of months
        :return:
        List containing [("yyyy-mm-dd", Day object)]
        """
        month_list = list()
        if (start_day.month + month_count) > 12:
            year_list = self.get_year(start_day.year)
            year_list.extend(self.get_year((start_day.year + 1)))
        else:
            year_list = self.get_year(start_day.year)

        search_list = self.compose_search_list(start_day, month_count)
        for day_tuple in year_list:
            day = day_tuple[1]
            if [day.month, day.year] in search_list:
                month_list.append(day_tuple)

        return month_list

    def get_week_days(self, start_day, month_count=1):
        """
        Gets all the date strings from today until the end of the month.
        :param month_count: number of months
        :param start_day: Day object
        :return: list of date string
        """
        return [day_tuple[0] for day_tuple in self.get_month_range(start_day, month_count) if
                day_tuple[1].to_date_time() > start_day.to_date_time()]

    def get_week_day_list(self, start_day, weekday_number, month_count):
        """
        Returns all the date strings for the provided week day in a month.
        :param start_day: Day object
        :param weekday_number: integer (ie. 0-6) m=0 and su=6
        :param month_count: number of months
        :return:
        list of date strings yyyy-mm-dd
        """
        return [day_tuple[0] for day_tuple in self.get_month_range(start_day, month_count) if
                day_tuple[1].weekday_number == weekday_number and day_tuple[1].to_date_time() > start_day.to_date_time()]

    def get_work_week_dates(self, start_day, month_count):
        """
        Gets all date strings within a work week from today until the end of the month
        :param start_day: Day object
        :param month_count: number of months
        :return: list of date strings
        """
        date_list = list()
        for i in [0, 1, 2, 3, 4]:
            for date_string in self.get_week_day_list(start_day, i, month_count):
                date_list.append(date_string)
        return sorted(date_list)

    @staticmethod
    def get_week_count(month, year):
        return len(calendar.monthcalendar(year, month))

    def diff(self, today, weekday_number):
        """
        Calculates the difference between the provided day and the calendar day with
        the provided weekday number
        :param today: Day object
        :param weekday_number: integer (ie. 0-6) m=0, su=6
        :return:
        """
        assert type(today) is Day

        if 0 <= weekday_number <= 6:
            # Check for weekday_number in the current week
            days_list = self.get_remaining_days_in_week(today)
            # Remaining days in current week
            remaining_days = len(days_list)
            # Weeks in current month
            week_count = self.get_week_count(today.month, today.year)
            if today.week < week_count:
                # If the weekday_number is in the current week then
                # return the diff in days between today and desired day
                if weekday_number in days_list:
                    day_count = days_list.index(weekday_number)
                    return day_count + 1
                else:
                    # If the weekday_number is in the next week then
                    # return the diff in days between today and desired day
                    # and add the days remaining from this week
                    day_count = self.weekday_list.index(weekday_number)
                    return remaining_days + (day_count + 1)
            else:
                # If the weekday_number is in the next month then
                # return the diff in days between today and desired day
                # and add the days remaining from this week
                day_count = self.weekday_list.index(weekday_number)
                return remaining_days + (day_count + 1)

    def get_next_day(self, today, weekday_number):
        """
        Gets the next calendar day in current week, next week, or next month that
        matches the provided weekday_number.
        :param weekday_number: integer (ie. 0-6) m=0, su=6
        :return: Day object
        """
        day_count = self.diff(today, weekday_number)
        today = today.to_date_time()
        future_day = today + timedelta(days=day_count)
        return Day(future_day)

    @staticmethod
    def get_remaining_days_in_week(today):
        """
        Determines the remaining days from today until the end of the week.
        :param today:
        :return: list of weekdays (ie. 0-6) m=0, su=6
        """
        remaining_days = list()
        for week_count, week_list in enumerate(calendar.Calendar().monthdays2calendar(today.year, today.month),
                                               start=1):
            if today.week == week_count:
                for day_tuple in week_list:
                    if day_tuple[1] > today.weekday_number:
                        remaining_days.append(day_tuple[1])
        return remaining_days

    def get_first_day_of_month(self, start_day, month_count):
        """
        Returns a list containing the first day from each month.
        :param start_day:
        :param month_count:
        :return:
        """
        return [day_tuple[0] for day_tuple in self.get_month_range(start_day, month_count) if
                day_tuple[1].day == 1]

    def get_last_day_of_month(self, start_day, month_count):
        """
        Returns a list containing the last day from each month
        :param start_day:
        :param month_count:
        :return:
        """
        last_day_list = list()
        for day_tuple in self.get_month_range(start_day, month_count):
            day = day_tuple[1]
            last_day_in_month = self.get_day_count(day)
            if day.day == last_day_in_month:
                last_day_list.append(day_tuple[0])
        return last_day_list

    @staticmethod
    def get_day_count(day):
        return calendar.monthrange(day.year, day.month)[1]
