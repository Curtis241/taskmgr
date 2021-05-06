import unittest
from datetime import datetime

from taskmgr.lib.model.calendar import Calendar
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.model.day import Day
from taskmgr.lib.variables import CommonVariables


class TestCalendar(unittest.TestCase):

    @staticmethod
    def from_date_string_list(date_string_list):
        due_date_list = list()
        if type(date_string_list) is list and len(date_string_list) > 0:
            for date_string in date_string_list:
                if type(date_string) is str:
                    dd = DueDate()
                    dd.date_string = date_string
                    dd.completed = False
                    due_date_list.append(dd)
        return due_date_list

    def setUp(self) -> None:
        self.calendar = Calendar()
        self.vars = CommonVariables()
        self.march1 = datetime.strptime('2019-03-01', self.vars.date_format)
        self.march31 = datetime.strptime('2019-03-31', self.vars.date_format)
        self.may31 = datetime.strptime('2019-05-31', self.vars.date_format)
        self.dec1 = datetime.strptime("2019-12-01", self.vars.date_format)
        self.dec31 = datetime.strptime("2019-12-31", self.vars.date_format)

    def tearDown(self) -> None: pass

    def test_get_week_count(self):
        self.assertTrue(self.calendar.get_week_count(3, 2019) == 5)

    def test_get_last_day(self):
        day_list = self.calendar.get_last_day_of_month(Day(self.march1), 1)
        self.assertListEqual(day_list, ['2019-03-31'])

    def test_get_last_day_for_three_months(self):
        day_list = self.calendar.get_last_day_of_month(Day(self.dec1), 3)
        self.assertListEqual(day_list, ['2019-12-31', '2020-01-31', '2020-02-29'])

    def test_get_first_day_for_three_months(self):
        day_list = self.calendar.get_first_day_of_month(Day(self.dec1), 3)
        self.assertListEqual(day_list, ['2019-12-01', '2020-01-01', '2020-02-01'])

    def test_get_weekday_number(self):
        self.assertIsNone(self.calendar.get_weekday_number("today"))
        self.assertTrue(self.calendar.get_weekday_number("m") == 0)

    def test_get_next_year(self):
        date_list = self.calendar.get_year(2020)
        self.assertTrue(len(date_list) == 366)

    def test_get_current_year(self):
        date_list = self.calendar.get_year(2019)
        self.assertTrue(len(date_list) == 365)

    def test_get_month(self):
        date_list = self.calendar.get_week_days(Day(self.dec1))
        self.assertTrue(len(date_list) == 30)

    def test_get_month_range(self):
        date_list = self.calendar.get_month_range(self.dec1, 3)
        print(len(date_list))

    def test_compose_search_list(self):
        search_list = self.calendar.compose_search_list(Day(self.dec1), 3)
        self.assertListEqual(search_list, [[12, 2019], [1, 2020], [2, 2020]])

        search_list = self.calendar.compose_search_list(Day(self.march31), 5)
        self.assertListEqual(search_list, [[3, 2019], [4, 2019], [5, 2019], [6, 2019], [7, 2019]])

        search_list = self.calendar.compose_search_list(Day(self.dec31), 1)
        self.assertListEqual(search_list, [[12, 2019]])

    def test_month_range(self):
        month_list = self.calendar.get_month_range(Day(self.dec1), 3)
        self.assertTrue(len(month_list) == 91)

        month_list = self.calendar.get_month_range(Day(self.dec1), 1)
        self.assertTrue(len(month_list) == 31)

    def test_get_closest_date(self):
        day_list = self.calendar.get_first_day_of_month(Day(self.march1), 10)
        due_date_list = self.from_date_string_list(day_list)
        current_date_time = datetime.strptime('2019-04-17', self.vars.date_format)
        due_date = self.calendar.get_closest_due_date(due_date_list, Day(current_date_time))
        self.assertTrue(due_date.date_string == "2019-05-01")

    def test_contains_week(self):
        day = Day(datetime.strptime("2021-04-14", self.vars.date_format))
        result = self.calendar.contains_week([DueDate("2021-04-14"), DueDate("2021-04-21")], day)
        self.assertTrue(result)

    def test_contains_day(self):
        day = Day(datetime.strptime("2021-04-14", self.vars.date_format))
        result = self.calendar.contains_month([DueDate("2021-04-14"), DueDate("2021-04-21")], day)
        self.assertTrue(result)