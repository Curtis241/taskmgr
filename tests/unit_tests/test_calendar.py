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
        self.march1 = Day(datetime.strptime('2019-03-01', self.vars.date_format))
        self.march31 = Day(datetime.strptime('2019-03-31', self.vars.date_format))
        self.may31 = Day(datetime.strptime('2019-05-31', self.vars.date_format))
        self.dec1 = Day(datetime.strptime("2019-12-01", self.vars.date_format))
        self.dec31 = Day(datetime.strptime("2019-12-31", self.vars.date_format))

        self.june4 = Day(datetime.strptime("2021-06-04", self.vars.date_format))
        self.june7 = Day(datetime.strptime("2021-06-07", self.vars.date_format))
        self.june9 = Day(datetime.strptime("2021-06-09", self.vars.date_format))
        self.june11 = Day(datetime.strptime("2021-06-11", self.vars.date_format))
        self.june29 = Day(datetime.strptime("2021-07-02", self.vars.date_format))

    def tearDown(self) -> None: pass

    def test_get_weekday_number(self):
        self.assertIsNone(self.calendar.get_weekday_number("today"))
        self.assertTrue(self.calendar.get_weekday_number("m") == 0)

    def test_get_days_for_one_month(self):
        day_list = self.calendar.get_days(self.dec1, 1)
        self.assertTrue(len(day_list) == 32)

    def test_get_days_for_three_months(self):
        day_list = self.calendar.get_days(self.dec1, 3)
        self.assertTrue(len(day_list) == 92)

    def test_contains_week(self):
        day = Day(datetime.strptime("2021-04-14", self.vars.date_format))
        result = self.calendar.contains_week([DueDate("2021-04-14"), DueDate("2021-04-21")], day)
        self.assertTrue(result)

    def test_contains_day(self):
        day = Day(datetime.strptime("2021-04-14", self.vars.date_format))
        result = self.calendar.contains_month([DueDate("2021-04-14"), DueDate("2021-04-21")], day)
        self.assertTrue(result)

    def test_get_day_using_abbrev(self):
        day = self.calendar.get_day_using_abbrev(self.march1, "m")
        self.assertTrue(day.to_date_string() == "2019-03-04")

    def test_get_start_and_end_of_month(self):
        start_day = self.calendar.get_first_day_in_month(self.march1)
        self.assertEqual(start_day.to_date_string(), "2019-03-01")
        last_day = self.calendar.get_last_day_in_month(self.march1)
        self.assertEqual(last_day.to_date_string(), "2019-03-31")

    def test_get_start_of_week(self):
        new_day = self.calendar.get_first_day_in_week(self.june4)
        self.assertEqual(new_day.to_date_string(), "2021-05-31")

        new_day = self.calendar.get_first_day_in_week(self.june9)
        self.assertEqual(new_day.to_date_string(), "2021-06-07")

        new_day = self.calendar.get_first_day_in_week(self.june7)
        self.assertEqual(new_day.to_date_string(), "2021-06-07")

        new_day = self.calendar.get_first_day_in_week(self.june11)
        self.assertEqual(new_day.to_date_string(), "2021-06-07")

    def test_get_end_of_week(self):
        new_day = self.calendar.get_last_day_in_week(self.june9)
        self.assertEqual(new_day.to_date_string(), "2021-06-13")

        new_day = self.calendar.get_last_day_in_week(self.june7)
        self.assertEqual(new_day.to_date_string(), "2021-06-13")

        new_day = self.calendar.get_last_day_in_week(self.june11)
        self.assertEqual(new_day.to_date_string(), "2021-06-13")

        new_day = self.calendar.get_last_day_in_week(self.june29)
        self.assertEqual(new_day.to_date_string(), "2021-07-04")

    def test_is_short_date(self):
        self.assertTrue(self.calendar.is_short_date("May 21"))
        self.assertFalse(self.calendar.is_short_date("Jun 41"))
        self.assertFalse(self.calendar.is_short_date("April 1"))

    def test_parse_short_date(self):
        day = self.calendar.parse_date("May 21")
        self.assertEqual(day.to_date_string(), "2021-05-21")

    def test_parse_recurring_abbrev(self):
        day_list = self.calendar.parse_recurring_abbrev(self.june11, "every m", 3)
        self.assertTrue(len(day_list) == 13)
        self.assertTrue(day_list[0].to_date_string() == "2021-06-14")
        self.assertTrue(day_list[1].to_date_string() == "2021-06-21")
        self.assertTrue(day_list[2].to_date_string() == "2021-06-28")
        self.assertTrue(day_list[12].to_date_string() == "2021-09-06")

    def test_get_last_week(self):
        day_list = self.calendar.get_last_week(self.june11)
        self.assertTrue(len(day_list) == 7)
        self.assertTrue(day_list[0].to_date_string() == "2021-05-31")
        self.assertTrue(day_list[-1].to_date_string() == "2021-06-06")

    def test_get_this_week(self):
        day_list = self.calendar.get_this_week(self.june11)
        self.assertTrue(len(day_list) == 7)
        self.assertTrue(day_list[0].to_date_string() == "2021-06-07")
        self.assertTrue(day_list[-1].to_date_string() == "2021-06-13")

        day_list = self.calendar.get_this_week(self.june7)
        self.assertTrue(len(day_list) == 7)
        self.assertTrue(day_list[0].to_date_string() == "2021-06-07")
        self.assertTrue(day_list[-1].to_date_string() == "2021-06-13")

    def test_get_next_week(self):
        day_list = self.calendar.get_next_week(self.june11)
        self.assertTrue(len(day_list) == 7)
        self.assertTrue(day_list[0].to_date_string() == "2021-06-14")
        self.assertTrue(day_list[-1].to_date_string() == "2021-06-20")

        day_list = self.calendar.get_next_week(self.june29)
        self.assertTrue(len(day_list) == 7)
        self.assertTrue(day_list[0].to_date_string() == "2021-07-05")
        self.assertTrue(day_list[-1].to_date_string() == "2021-07-11")

    def test_get_this_month(self):
        day_list = self.calendar.get_this_month(self.june7)
        self.assertTrue(len(day_list) == 30)
        self.assertTrue(day_list[0].to_date_string() == "2021-06-01")
        self.assertTrue(day_list[-1].to_date_string() == "2021-06-30")

    def test_get_next_month(self):
        day_list = self.calendar.get_next_month(self.june7)
        self.assertTrue(len(day_list) == 31)
        self.assertTrue(day_list[0].to_date_string() == "2021-07-01")
        self.assertTrue(day_list[-1].to_date_string() == "2021-07-31")

    def test_get_last_month(self):
        day_list = self.calendar.get_last_month(self.june7)
        self.assertTrue(len(day_list) == 31)
        self.assertTrue(day_list[0].to_date_string() == "2021-05-01")
        self.assertTrue(day_list[-1].to_date_string() == "2021-05-31")