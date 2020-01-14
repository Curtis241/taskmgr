import calendar
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from taskmgr.lib.variables import CommonVariables


class DueDate(object):
    """The DueDate object was created to support reoccurring tasks. When there are many dates each
    date can be marked as completed."""

    def __init__(self):
        self.__completed = False
        self.__date_string = str()

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, is_completed):
        assert type(is_completed) is bool
        self.__completed = is_completed

    @property
    def date_string(self):
        return self.__date_string

    @date_string.setter
    def date_string(self, date_string):
        """
        Store a datetime object converted to a date string using a formatter.
        See the CommonVariables.date_format formatter
        :param date_string:
        :return:
        """
        assert type(date_string) is str
        self.__date_string = date_string

    def to_dict(self):
        """
        Converts object to dict
        :return:  dict
        """
        return {"date_string": self.__date_string, "completed": self.__completed}

    def from_dict(self, due_date_dict):
        """
        Converts dict to object
        :param due_date_dict: DueDate dict
        :return: DueDate object
        """
        if "date_string" in due_date_dict:
            self.__date_string = due_date_dict["date_string"]

        if "completed" in due_date_dict:
            self.__completed = due_date_dict["completed"]

        return self


class Day:
    def __init__(self, dt):
        assert type(dt) is datetime
        self.dt = dt
        self.day = dt.day
        self.month = dt.month
        self.year = dt.year
        self.timestamp = dt.timestamp()
        self.weekday_number = dt.weekday()
        self.week = self.get_week(self.day, self.weekday_number, self.month, self.year)
        self.vars = CommonVariables()

    def to_date_list(self):
        return [self.to_date_string()]

    def to_date_expression(self):
        return f"{self.month} {self.day}"

    def to_date_string(self):
        month = Day.pad(self.month)
        day = Day.pad(self.day)
        return f"{self.year}-{month}-{day}"

    def to_date_time_string(self):
        return datetime.strftime(self.dt, self.vars.date_time_format)

    def to_date_time(self):
        month = self.pad(self.month)
        day = self.pad(self.day)
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
    def __exists(day_tuple, date_list):
        for d in date_list:
            if d[0] == day_tuple[0]:
                return True
        return False

    def __add(self, day, date_list):
        day_tuple = (day.to_date_string(), day)
        if not self.__exists(day_tuple, date_list):
            date_list.append(day_tuple)
        return date_list

    def is_past(self, due_date, current_day=Today()):
        if type(due_date) is DueDate and len(due_date.date_string) > 0:
            day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))
            timedelta1 = day.to_date_time() - current_day.to_date_time()
            if timedelta1.days < 0:
                return True

        return False

    def contains_month(self, due_date_list, selected_day=Today()):
        for due_date in due_date_list:
            day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))
            if day.month == selected_day.month:
                return True
        return False

    def contains_week(self, due_date_list, selected_day=Today()):
        for due_date in due_date_list:
            day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))
            if day.week == selected_day.week:
                return True
        return False

    @staticmethod
    def contains_due_date(due_date_list, date_string):
        """
        Looks for today's date in provided list of date strings
        :param due_date_list: ["2019-01-01", "2019-01-02", "2019-01-03"]
        :param date_string: "2019-01-02"
        :return:
        Boolean value
        """
        assert type(due_date_list) is list
        assert type(date_string) is str

        for due_date in due_date_list:
            if due_date.date_string == date_string:
                return True
        return False

    def contains_due_date_range(self, min_date_string, max_date_string, due_date_list):

        for due_date in due_date_list:
            min_day = Day(datetime.strptime(min_date_string, self.vars.date_format))
            max_day = Day(datetime.strptime(max_date_string, self.vars.date_format))
            if len(due_date.date_string) > 0:
                day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))

                if min_day.to_date_time() < day.to_date_time() < max_day.to_date_time():
                    return True
        return False

    def get_closest_due_date(self, due_date_list, current_day=None):
        """
        Returns a future date string that is the closest to the current day
        :param due_date_list: list of due_date objects with the format yyyy-mm-dd
        :param current_day: Day object
        :return:
        Date string
        """
        if current_day is None:
            current_day = Today()

        if type(due_date_list) is list and len(due_date_list) > 0:
            diff_list = []

            if type(due_date_list[0]) is DueDate:
                # calculate the difference between current day and date string
                for due_date in due_date_list:
                    if len(due_date.date_string) > 0:
                        day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))
                        timedelta1 = day.to_date_time() - current_day.to_date_time()
                        diff_list.append(timedelta1.days)

                # return the date string using the smallest difference
                for index, diff_num in enumerate(diff_list):
                    if diff_num >= 0:
                        return due_date_list[index]
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

    def get_work_week_dates(self, today, month_count):
        """
        Gets all date strings within a work week from today until the end of the month
        :param today: Day object
        :return: list of date strings
        """
        date_list = list()
        for i in [0, 1, 2, 3, 4]:
            date_list.extend(self.get_week_days(today, i, month_count))
        return date_list

    def get_months(self, start_day, month_count=1):
        """
        Gets all the date strings from today until the end of the month.
        :param month_count: number of months
        :param start_day: Day object
        :return: list of date strings
        """
        return [day_tuple[0] for day_tuple in self.get_month_range(start_day, month_count) if
                day_tuple[1].to_date_time() > start_day.to_date_time()]

    def get_week_days(self, today, weekday_number, month_count):
        """
        Returns all the date strings for the provided week day in a month.
        :param today: Day object
        :param weekday_number: integer (ie. 0-6) m=0, su=6
        :param month_count: number of months
        :return:
        list of date strings yyyy-mm-dd
        """
        return [day_tuple[0] for day_tuple in self.get_month_range(today, month_count) if
                day_tuple[1].weekday_number == weekday_number]

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


class DateParser:

    def __init__(self, expression, day):
        assert type(expression) is str
        self.expression = str(expression).lower()
        self.today = day
        self.date_list = []
        self.handler_name = str()
        self.calendar = Calendar()


class Handler(ABC):
    def __init__(self):
        self.next_handler = None

    def handle(self, request):
        self.next_handler.handle(request)

    @abstractmethod
    def parse_expression(self, parser): pass

    @abstractmethod
    def validate(self, expression): pass


class DayOfWeekHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ['su', 'm', 'tu', 'w', 'th', 'f', 'sa']

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(DayOfWeekHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = DayOfWeekHandler.__name__
        weekday_number = parser.calendar.get_weekday_number(parser.expression)
        calendar_day = parser.calendar.get_next_day(parser.today, weekday_number)
        parser.date_list = calendar_day.to_date_list()

    def validate(self, expression):
        return expression in self.expression_list


class NormalLanguageDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["today", "tomorrow", "next week", "next month"]

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(NormalLanguageDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = NormalLanguageDateHandler.__name__

        if parser.expression == "today":
            date_list = parser.today.to_date_list()
            parser.date_list = date_list

        if parser.expression == "tomorrow":
            today = parser.today
            tomorrow = today.to_date_time() + timedelta(days=1)
            parser.date_list = Day(tomorrow).to_date_list()

        if parser.expression == "next week":
            calendar_day = parser.calendar.get_next_day(parser.today, 0)
            parser.date_list = calendar_day.to_date_list()

        if parser.expression == "next month":
            today = parser.today
            today.month = today.month + 1
            parser.date_list = parser.calendar.get_first_day_of_month(today, 1)

    def validate(self, expression):
        return expression in self.expression_list


class RecurringDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["every day", "every weekday", "every su", "every m", "every tu", "every w", "every th",
                                "every f", "every sa"]
        self.week_abbrev_list = ['su', 'm', 'tu', 'w', 'th', 'f', 'sa']
        self.vars = CommonVariables()

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(RecurringDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = RecurringDateHandler.__name__
        if parser.expression == "every day":
            date_list = parser.calendar.get_months(parser.today, self.vars.recurring_month_limit)
            parser.date_list = date_list

        elif parser.expression == "every weekday":
            parser.date_list = parser.calendar.get_work_week_dates(parser.today,
                                                                   self.vars.recurring_month_limit)
        elif str(parser.expression).startswith("every"):
            expression = str(parser.expression).split(" ")
            if expression[1] in self.week_abbrev_list:
                weekday_number = parser.calendar.get_weekday_number(expression[1])
                parser.date_list = parser.calendar.get_week_days(parser.today, weekday_number,
                                                                 self.vars.recurring_month_limit)

    def validate(self, expression):
        return expression in self.expression_list


class ShortDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(ShortDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        expression = str(parser.expression).lower().split(" ")
        for month_number, month in enumerate(self.expression_list, start=1):
            if expression[0] == month and int(expression[1]) in range(1, calendar.mdays[month_number]):
                now = datetime.now()
                day = Day(now)
                day.month = month_number
                day.day = int(expression[1])
                parser.date_list = day.to_date_list()

    def validate(self, expression):
        fragments = str(expression).lower().split(" ")
        if len(fragments) == 2:
            month_exists = fragments[0] in self.expression_list
            day_number_exists = str(fragments[1]).isdigit()
            return month_exists is True and day_number_exists is True
        else:
            return False


class EmptyDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ['empty']

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(EmptyDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.date_list = []

    def validate(self, expression):
        return expression in self.expression_list


class ErrorHandler(Handler):

    def validate(self, expression):
        pass

    def parse_expression(self, parser):
        pass

    def handle(self, parser):
        print("Invalid request: expression {}".format(parser.expression))


class DateGenerator(object):

    def __init__(self):
        self.__current_day = None
        self.handler_1 = DayOfWeekHandler()
        self.handler_2 = NormalLanguageDateHandler()
        self.handler_3 = RecurringDateHandler()
        self.handler_4 = ShortDateHandler()
        self.handler_5 = EmptyDateHandler()
        self.handler_list = [self.handler_1, self.handler_2, self.handler_3, self.handler_4, self.handler_5]

    @property
    def current_day(self):
        if self.__current_day is None:
            return Day(datetime.now())
        else:
            return self.__current_day

    @current_day.setter
    def current_day(self, current_day):
        self.__current_day = current_day

    def get_due_dates(self, expression):

        assert type(expression) is str
        parser = DateParser(expression, self.current_day)

        self.handler_1.next_handler = self.handler_2
        self.handler_2.next_handler = self.handler_3
        self.handler_3.next_handler = self.handler_4
        self.handler_4.next_handler = self.handler_5
        self.handler_5.next_handler = ErrorHandler()
        self.handler_1.handle(parser)

        due_date_list = list()
        if len(parser.date_list) == 0:
            due_date = DueDate()
            due_date.date_string = ""
            due_date.completed = False
            due_date_list.append(due_date)
        else:
            for date_string in parser.date_list:
                due_date = DueDate()
                due_date.date_string = date_string
                due_date.completed = False
                due_date_list.append(due_date)

        return due_date_list

    def validate_input(self, date_expression):

        for handler in self.handler_list:
            if handler.validate(date_expression):
                return True

        return False
