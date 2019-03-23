import calendar
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from taskmgr.lib.variables import CommonVariables


class Day:
    def __init__(self, dt):
        assert type(dt) is datetime
        self.day = dt.day
        self.month = dt.month
        self.year = dt.year
        self.weekday_number = dt.weekday()
        week = self.get_week(self.day, self.weekday_number, self.month, self.year)
        self.week = week

    def to_date_list(self):
        month = Day.pad(self.month)
        day = Day.pad(self.day)
        return ["{}-{}-{}".format(self.year, month, day)]

    def to_date_time(self):
        month = self.pad(self.month)
        day = self.pad(self.day)
        return datetime.strptime("{}-{}-{}".format(self.year, month, day), CommonVariables.date_format)

    @staticmethod
    def pad(value):
        if len(str(value)) == 1:
            return "{0:0=2d}".format(value)
        return str(value)

    @staticmethod
    def get_day(weekday_number, week, month, year):
        cal = calendar.Calendar()
        for week_count, week_list in enumerate(cal.monthdays2calendar(year, month), start=1):
            for day_tuple in week_list:
                if week_count == week and day_tuple[1] == weekday_number:
                    return day_tuple[0]

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


class DateParser:

    def __init__(self, expression, day):
        assert type(expression) is str
        self.expression = str(expression).lower()
        self.weekday_list = range(0, 6)
        self.month_list = range(1, 12)
        self.weekdays_list = [('su', 6), ('m', 0), ('tu', 1), ('w', 2), ('th', 3), ('f', 4), ('sa', 5)]
        self.today = day
        self.date_list = []

    def get_weekday_number(self, day_abbrev):
        day_tuple = [e[1] for e in self.weekdays_list if day_abbrev == e[0]]
        if len(day_tuple) == 0:
            return None
        else:
            return day_tuple[0]

    @staticmethod
    def get_week_count(month, year):
        return len(calendar.monthcalendar(year, month))

    @staticmethod
    def get_remaining_days(today):
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

    @staticmethod
    def get_last_day(today):
        """
        Gets the last day in the month.
        :param today: Day object
        :return: last day in current month.
        """
        return calendar.monthrange(today.year, today.month)[1]

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
            days_list = DateParser.get_remaining_days(today)
            # Remaining days in current week
            remaining_days = len(days_list)
            # Weeks in current month
            week_count = DateParser.get_week_count(today.month, today.year)
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

    def get_next_day(self, weekday_number):
        """
        Gets the next calendar day in current week, next week, or next month that
        matches the provided weekday_number.
        :param weekday_number: integer (ie. 0-6) m=0, su=6
        :return: Day object
        """
        day_count = self.diff(self.today, weekday_number)
        print("diff: day_count: {}".format(day_count))
        today = self.today.to_date_time()
        future_day = today + timedelta(days=day_count)
        return Day(future_day)

    @staticmethod
    def get_work_week_dates_in_month(today):
        """
        Gets all date strings within a work week from today until the end of the month
        :param today: Day object
        :return: list of date strings
        """
        date_list = list()
        for i in [0, 1, 2, 3, 4]:
            date_list.extend(DateParser.get_all_dates(today, i))
        return date_list

    @staticmethod
    def get_all_dates_in_month(today):
        """
        Gets all the date strings from today until the end of the month.
        :param today: Day object
        :return: list of date strings
        """
        date_list = list()
        for week_list in calendar.Calendar().monthdayscalendar(today.year, today.month):
            for day in week_list:
                if int(day) > int(today.day):
                    date_list.append("{}-{}-{}".format(today.year, today.month, day))
        return date_list

    @staticmethod
    def get_all_dates(today, weekday_number):

        date_list = list()
        for week_list in calendar.Calendar().monthdays2calendar(today.year, today.month):
            for day_tuple in week_list:
                if int(day_tuple[0]) > int(today.day) and day_tuple[1] == weekday_number:
                    date_list.append("{}-{}-{}".format(today.year, today.month, day_tuple[0]))
        return date_list


class Handler(ABC):
    def __init__(self):
        self.next_handler = None

    def handle(self, request):
        self.next_handler.handle(request)

    @abstractmethod
    def parse_expression(self, parser): pass


class DayOfWeekHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ['su', 'm', 'tu', 'w', 'th', 'f', 'sa']

    def handle(self, parser):
        if parser.expression in self.expression_list:
            self.parse_expression(parser)
        else:
            super(DayOfWeekHandler, self).handle(parser)

    def parse_expression(self, parser):
        print("Found match in {}!".format(DayOfWeekHandler.__name__))
        print("parse_expression: expression {}".format(parser.expression))
        weekday_number = parser.get_weekday_number(parser.expression)

        print("parse_expression: weekday_number {}".format(weekday_number))
        calendar_day = parser.get_next_day(weekday_number)

        date_list = calendar_day.to_date_list()
        print("parse_expression: date_list {}".format(date_list))
        parser.date_list = date_list


class NormalLanguageDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["today", "tomorrow", "next week", "next month"]

    def handle(self, parser):
        if parser.expression in self.expression_list:
            self.parse_expression(parser)
        else:
            super(NormalLanguageDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        print("Found match {}!".format(NormalLanguageDateHandler.__name__))
        print("parse_expression: expression {}".format(parser.expression))

        if parser.expression == "today":
            date_list = parser.today.to_date_list()
            print("parse_expression: date_list {}".format(date_list))
            parser.date_list = date_list

        if parser.expression == "tomorrow":
            today = parser.today
            tomorrow = today.to_date_time() + timedelta(days=1)
            parser.date_list = Day(tomorrow).to_date_list()

        if parser.expression == "next week":
            calendar_day = parser.get_next_day(0)
            date_list = calendar_day.to_date_list()
            print("parse_expression: date_list {}".format(date_list))
            parser.date_list = date_list

        if parser.expression == "next month":
            date_string = '{}-{}-{}'.format(parser.today.year, parser.today.month, parser.get_last_day(parser.today))
            parser.today = Day(datetime.strptime(date_string, CommonVariables.date_format))
            calendar_day = parser.get_next_day(0)
            parser.date_list = calendar_day.to_date_list()


class RecurringDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["every day", "every weekday", "every su", "every m", "every tu", "every w", "every th",
                                "every f", "every sa"]
        self.week_abbrev_list = ['su', 'm', 'tu', 'w', 'th', 'f', 'sa']

    def handle(self, parser):
        if parser.expression in self.expression_list:
            self.parse_expression(parser)
        else:
            super(RecurringDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        print("Found match {}!".format(RecurringDateHandler.__name__))

        if parser.expression == "every day":
            parser.date_list = parser.get_all_dates_in_month(parser.today)

        elif parser.expression == "every weekday":
            parser.date_list = parser.get_work_week_dates_in_month(parser.today)

        elif str(parser.expression).startswith("every"):
            expression = str(parser.expression).split(" ")
            if expression[1] in self.week_abbrev_list:
                weekday_number = parser.get_weekday_number(expression[1])
                parser.date_list = parser.get_all_dates(parser.today, weekday_number)


class ErrorHandler(Handler):
    def parse_expression(self, parser):
        pass

    def handle(self, parser):
        print("Invalid request")


class DateGenerator(object):

    def __init__(self, expression, current_date_time=Day(datetime.now())):
        assert type(expression) is str
        assert type(current_date_time) is Day

        self.expressions_list = []
        self.handler_1 = DayOfWeekHandler()
        self.handler_2 = NormalLanguageDateHandler()
        self.handler_3 = RecurringDateHandler()
        self.expressions_list.extend(self.handler_1.expression_list)
        self.expressions_list.extend(self.handler_2.expression_list)
        self.expressions_list.extend(self.handler_3.expression_list)

        if current_date_time is not None:
            self.parser = DateParser(expression, current_date_time)
        else:
            self.parser = DateParser(expression, Today())

    def get_expressions(self):
        return self.expressions_list

    def get_dates(self):
        self.handler_1.next_handler = self.handler_2
        self.handler_2.next_handler = self.handler_3
        self.handler_3.next_handler = ErrorHandler()
        self.handler_1.handle(self.parser)
        return self.parser.date_list
