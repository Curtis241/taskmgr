import unittest
from datetime import datetime

from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.calendar import Calendar, Today
from taskmgr.lib.model.task import DueDate
from taskmgr.lib.variables import CommonVariables


class TestDateGenerator(unittest.TestCase):

    def get_first_date_string(self, due_date_list):
        self.assertTrue(len(due_date_list) == 1)
        due_date = due_date_list[0]
        return due_date.date_string

    def get_date(self, current_date_string, date_expression, expected_date_string):

        current_date_time = datetime.strptime(current_date_string, CommonVariables().date_format)
        self.date_generator.current_day = Day(current_date_time)
        due_date_list = self.date_generator.get_due_dates(date_expression)
        return self.get_first_date_string(due_date_list) == expected_date_string

    def get_date_count(self, current_date_string, date_expression):
        current_date_time = datetime.strptime(current_date_string, CommonVariables().date_format)
        self.date_generator.current_day = Day(current_date_time)
        due_date_list = self.date_generator.get_due_dates(date_expression)
        return len(due_date_list)

    def from_date_string_list(self, date_string_list):
        due_date_list = list()
        if type(date_string_list) is list and len(date_string_list) > 0:
            for date_string in date_string_list:
                if type(date_string) is str:
                    dd = DueDate()
                    dd.date_string = date_string
                    dd.completed = False
                    due_date_list.append(dd)
        return due_date_list

    def setUp(self):
        self.today = Today()
        self.vars = CommonVariables()
        self.march1 = datetime.strptime('2019-03-01', self.vars.date_format)
        self.march31 = datetime.strptime('2019-03-31', self.vars.date_format)
        self.may31 = datetime.strptime('2019-05-31', self.vars.date_format)
        self.dec1 = datetime.strptime("2019-12-01", self.vars.date_format)
        self.dec31 = datetime.strptime("2019-12-31", self.vars.date_format)
        self.calendar = Calendar()
        self.date_generator = DateGenerator()

    def tearDown(self):
        pass

    def test_pad_number(self):
        current_date_time = datetime.strptime('2019-03-12', self.vars.date_format)
        day = Day(current_date_time)
        date_list = day.to_date_list()
        self.assertListEqual(date_list, ['2019-03-12'])

    def test_get_date_when_in_same_week(self):
        self.assertTrue(self.get_date('2019-03-12', 'w', '2019-03-13'))

    def test_get_date_when_in_next_week(self):
        self.assertTrue(self.get_date('2019-03-12', 'm', '2019-03-18'))

    def test_get_date_when_in_next_month(self):
        self.assertTrue(self.get_date('2019-03-29', 'tu', '2019-04-02'))

    def test_get_date_when_today(self):
        self.assertTrue(self.get_date(self.today.to_date_string(), 'today', self.today.to_date_string()))

    def test_get_date_when_tomorrow(self):
        self.assertTrue(self.get_date('2019-03-29', 'tomorrow', '2019-03-30'))

    def test_get_date_when_next_week(self):
        self.assertTrue(self.get_date('2019-03-17', 'next week', '2019-03-18'))
        self.assertTrue(self.get_date('2019-03-18', 'next week', '2019-03-25'))
        self.assertTrue(self.get_date('2019-03-29', 'next week', '2019-04-01'))

    def test_get_date_when_next_month(self):
        self.assertTrue(self.get_date('2019-07-02', 'next month', '2019-08-01'))
        self.assertTrue(self.get_date('2019-12-02', 'next month', '2020-01-01'))

    def test_get_date_when_every_day(self):
        self.date_generator.current_day = Day(self.march1)
        due_date_list = self.date_generator.get_due_dates("every day")
        self.assertTrue(len(due_date_list) == 60)

    def test_get_date_count_when_every_weekday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every weekday') == 42)

    def test_get_date_when_every_weekday(self):
        self.vars.recurring_month_limit = 2
        self.date_generator.current_day = Day(self.march1)
        due_date_list = self.date_generator.get_due_dates("every weekday")
        self.assertTrue(len(due_date_list) == 42)
        self.assertTrue(due_date_list[0].date_string == "2019-03-04")
        self.assertTrue(due_date_list[1].date_string == "2019-03-05")
        self.assertTrue(due_date_list[2].date_string == "2019-03-06")
        self.assertTrue(due_date_list[3].date_string == "2019-03-07")
        self.assertTrue(due_date_list[4].date_string == "2019-03-08")

    def test_get_date_when_every_sunday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every su') == 9)

    def test_get_date_when_every_monday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every m') == 9)

    def test_get_date_when_every_tuesday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every tu') == 9)

    def test_get_date_when_every_wednesday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every w') == 8)

    def test_get_date_when_every_thursday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every th') == 8)

    def test_get_date_when_every_friday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every f') == 8)

    def test_get_date_when_every_saturday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every sa') == 9)

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

    def test_short_date(self):
        due_date_list = self.date_generator.get_due_dates("apr 14")
        self.assertTrue(self.get_first_date_string(due_date_list) == '2020-04-14')

    def test_validate_input(self):
        self.assertTrue(self.date_generator.validate_input("every weekday"))
        self.assertTrue(self.date_generator.validate_input("every tu"))
        self.assertTrue(self.date_generator.validate_input("m"))
        self.assertTrue(self.date_generator.validate_input("today"))
        self.assertFalse(self.date_generator.validate_input("every"))
        self.assertFalse(self.date_generator.validate_input("24"))
        self.assertFalse(self.date_generator.validate_input("monday"))
        self.assertTrue(self.date_generator.validate_input("apr 21"))
        self.assertFalse(self.date_generator.validate_input("apr"))

    def test_empty_date_handler(self):
        due_date_list = self.date_generator.get_due_dates("empty")
        self.assertTrue(len(due_date_list) == 1)
        due_date = due_date_list[0]
        self.assertEqual(due_date.date_string, "")
        self.assertFalse(due_date.completed)

    def test_year_month_date_handler(self):
        due_date_list = self.date_generator.get_due_dates("2019-03-019")
        self.assertTrue(len(due_date_list) == 1)
        self.assertFalse(due_date_list[0].completed)

        due_date_list = self.date_generator.get_due_dates("2019-03-01")
        self.assertTrue(len(due_date_list) == 1)
        self.assertFalse(due_date_list[0].completed)
        self.assertTrue(due_date_list[0].date_string == "2019-03-01")


if __name__ == "__main__":
    unittest.main()
