from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from typing import Optional, List

from taskmgr.lib.model.calendar import Calendar
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.time import Time
from taskmgr.lib.variables import CommonVariables


class DateContainer:

    def __init__(self, expression, day):
        assert type(expression) is str
        self.expression = str(expression).lower()
        self.today = day
        self.day_list = []
        self.handler_name = str()


class Handler(ABC):

    SINGLE = "single"
    MULTIPLE = "multiple"

    def __init__(self):
        self.next_handler = None
        self.calendar = Calendar()
        self.vars = CommonVariables()

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
        parser.day_list = [self.calendar.get_day_using_abbrev(parser.today, parser.expression)]

    def validate(self, expression):
        return expression in self.expression_list


class NormalLanguageDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["today", "tomorrow", "yesterday"]

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(NormalLanguageDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = NormalLanguageDateHandler.__name__

        if parser.expression == "today":
            parser.day_list = [parser.today]

        if parser.expression == "tomorrow":
            parser.day_list = [self.calendar.get_tomorrow(parser.today)]

        if parser.expression == "yesterday":
            parser.day_list = [self.calendar.get_yesterday(parser.today)]

    def validate(self, expression):
        return expression in self.expression_list


class DateRangeHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["this week", "next week", "last week",
                                "this month", "next month", "last month"]

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(DateRangeHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = DateRangeHandler.__name__

        if parser.expression == "this week":
            parser.day_list = self.calendar.get_this_week(parser.today)

        if parser.expression == "next week":
            parser.day_list = self.calendar.get_next_week(parser.today)

        if parser.expression == "last week":
            parser.day_list = self.calendar.get_last_week(parser.today)

        if parser.expression == "this month":
            parser.day_list = self.calendar.get_this_month(parser.today)

        if parser.expression == "next month":
            parser.day_list = self.calendar.get_next_month(parser.today)

        if parser.expression == "last month":
            parser.day_list = self.calendar.get_last_month(parser.today)

    def validate(self, expression):
        return expression in self.expression_list


class RecurringDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.expression_list = ["every day", "every weekday", "every su", "every m", "every tu", "every w", "every th",
                                "every f", "every sa"]
        self.week_abbrev_list = ['su', 'm', 'tu', 'w', 'th', 'f', 'sa']

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(RecurringDateHandler, self).handle(parser)

    def parse_expression(self, parser):
        parser.handler_name = RecurringDateHandler.__name__
        if parser.expression == "every day":
            parser.day_list = self.calendar.get_days(parser.today,
                                                     self.vars.recurring_month_limit)
        elif parser.expression == "every weekday":
            parser.day_list = self.calendar.get_work_week_days(parser.today,
                                                               self.vars.recurring_month_limit)
        elif str(parser.expression).startswith("every"):
            parser.day_list = self.calendar.parse_recurring_abbrev(parser.today, parser.expression,
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
        parser.day_list = [self.calendar.parse_date_time(parser.expression)]

    def validate(self, expression):
        return self.calendar.is_short_date(expression)


class YearMonthDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.vars = CommonVariables()

    def validate(self, expression):
        format_valid = self.vars.validate_date_format(expression)
        date_valid = self.calendar.is_valid(expression)
        return format_valid is True and date_valid is True

    def parse_expression(self, parser):
        parser.handler_name = YearMonthDateHandler.__name__
        parser.day_list = [self.calendar.parse_date_time(parser.expression)]

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(YearMonthDateHandler, self).handle(parser)


class ErrorHandler(Handler):

    def validate(self, expression):
        pass

    def parse_expression(self, parser):
        pass

    def handle(self, parser):
        print("Invalid request: expression {}".format(parser.expression))


class DateTimeGenerator(object):

    def __init__(self):
        self.vars = CommonVariables()
        self.__current_day = None
        self.handler_1 = DayOfWeekHandler()
        self.handler_2 = NormalLanguageDateHandler()
        self.handler_3 = RecurringDateHandler()
        self.handler_4 = ShortDateHandler()
        self.handler_5 = YearMonthDateHandler()
        self.handler_6 = DateRangeHandler()
        self.multiple_date_handler_list = [self.handler_1,
                                           self.handler_2,
                                           self.handler_3,
                                           self.handler_4,
                                           self.handler_5,
                                           self.handler_6]
        self.single_date_handler_list = [self.handler_1,
                                         self.handler_2,
                                         self.handler_4,
                                         self.handler_5]

    @property
    def current_day(self):
        if self.__current_day is None:
            return Day(datetime.now())
        else:
            return self.__current_day

    @current_day.setter
    def current_day(self, current_day):
        self.__current_day = current_day

    @staticmethod
    def get_time(expression: str) -> Optional[Time]:
        assert type(expression) is str
        day = Calendar().parse_date_time(expression)
        return Time(day.to_datetime())

    def get_day(self, expression: str) -> Optional[Day]:
        assert type(expression) is str
        parser = DateContainer(expression, self.current_day)

        self.handler_1.next_handler = self.handler_2
        self.handler_2.next_handler = self.handler_4
        self.handler_4.next_handler = self.handler_5
        self.handler_5.next_handler = ErrorHandler()
        self.handler_1.handle(parser)

        if len(parser.day_list) == 1:
            return deque(parser.day_list).popleft()
        return None

    def get_days(self, expression: str) -> List[Day]:
        assert type(expression) is str
        parser = DateContainer(expression, self.current_day)

        self.handler_1.next_handler = self.handler_2
        self.handler_2.next_handler = self.handler_3
        self.handler_3.next_handler = self.handler_4
        self.handler_4.next_handler = self.handler_5
        self.handler_5.next_handler = self.handler_6
        self.handler_6.next_handler = ErrorHandler()
        self.handler_1.handle(parser)
        return parser.day_list

    def validate_input(self, date_expression: str,
                       single_date: bool = False) -> bool:

        if date_expression is None:
            return False

        if single_date:
            handler_list = self.single_date_handler_list
        else:
            handler_list = self.multiple_date_handler_list

        for handler in handler_list:
            if handler.validate(date_expression):
                return True
        return False
