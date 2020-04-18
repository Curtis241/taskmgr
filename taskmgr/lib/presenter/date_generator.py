import calendar
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.calendar import Calendar

from taskmgr.lib.variables import CommonVariables


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
            date_list = parser.calendar.get_week_days(parser.today, self.vars.recurring_month_limit)
            parser.date_list = date_list

        elif parser.expression == "every weekday":
            parser.date_list = parser.calendar.get_work_week_dates(parser.today,
                                                                   self.vars.recurring_month_limit)
        elif str(parser.expression).startswith("every"):
            expression = str(parser.expression).split(" ")
            if expression[1] in self.week_abbrev_list:
                weekday_number = parser.calendar.get_weekday_number(expression[1])
                parser.date_list = parser.calendar.get_week_day_list(parser.today, weekday_number,
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


class YearMonthDateHandler(Handler):

    def __init__(self):
        super().__init__()
        self.vars = CommonVariables()

    def validate(self, expression):
        return self.vars.validate_date_format(expression)

    def parse_expression(self, parser):
        parser.handler_name = YearMonthDateHandler.__name__
        parser.date_list = [parser.expression]

    def handle(self, parser):
        if self.validate(parser.expression):
            self.parse_expression(parser)
        else:
            super(YearMonthDateHandler, self).handle(parser)


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
        self.handler_5 = YearMonthDateHandler()
        self.handler_6 = EmptyDateHandler()
        self.handler_list = [self.handler_1, self.handler_2, self.handler_3, self.handler_4,
                             self.handler_5, self.handler_6]

    @property
    def current_day(self):
        if self.__current_day is None:
            return Day(datetime.now())
        else:
            return self.__current_day

    @current_day.setter
    def current_day(self, current_day):
        self.__current_day = current_day

    def get_due_dates(self, expression: str) -> list:
        assert type(expression) is str
        parser = DateParser(expression, self.current_day)

        self.handler_1.next_handler = self.handler_2
        self.handler_2.next_handler = self.handler_3
        self.handler_3.next_handler = self.handler_4
        self.handler_4.next_handler = self.handler_5
        self.handler_5.next_handler = self.handler_6
        self.handler_6.next_handler = ErrorHandler()
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

    def validate_input(self, date_expression: str) -> bool:
        assert type(date_expression) is str
        for handler in self.handler_list:
            if handler.validate(date_expression):
                return True
        return False
