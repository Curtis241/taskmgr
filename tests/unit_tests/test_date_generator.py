import unittest
from datetime import datetime

from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.variables import CommonVariables


class TestDateGenerator(unittest.TestCase):

    def match_date(self, current_date_string, date_expression, expected_date_string):
        current_date_time = datetime.strptime(current_date_string, CommonVariables().date_format)
        self.date_generator.current_day = Day(current_date_time)
        due_date_list = self.date_generator.get_due_dates(date_expression)
        return due_date_list[0].date_string == expected_date_string

    def get_date_count(self, current_date_string, date_expression):
        current_date_time = datetime.strptime(current_date_string, CommonVariables().date_format)
        self.date_generator.current_day = Day(current_date_time)
        due_date_list = self.date_generator.get_due_dates(date_expression)
        return len(due_date_list)

    def setUp(self):
        self.today = Today()
        self.vars = CommonVariables()
        self.date_generator = DateGenerator()
        self.march1 = datetime.strptime('2019-03-01', self.vars.date_format)

    def tearDown(self):
        pass

    def test_pad_number(self):
        current_date_time = datetime.strptime('2019-03-12', self.vars.date_format)
        day = Day(current_date_time)
        date_list = day.to_date_list()
        self.assertListEqual(date_list, ['2019-03-12'])

    def test_get_date_when_in_same_week(self):
        self.assertTrue(self.match_date('2019-03-12', 'w', '2019-03-13'))

    def test_get_date_when_in_next_week(self):
        self.assertTrue(self.match_date('2019-03-12', 'm', '2019-03-18'))

    def test_get_date_when_in_next_month(self):
        self.assertTrue(self.match_date('2019-03-29', 'tu', '2019-04-02'))

    def test_get_date_when_today(self):
        self.assertTrue(self.match_date(self.today.to_date_string(), 'today', self.today.to_date_string()))

    def test_get_date_when_tomorrow(self):
        self.assertTrue(self.match_date('2019-03-29', 'tomorrow', '2019-03-30'))

    def test_get_date_when_next_week(self):
        self.assertTrue(self.match_date('2019-03-17', 'next week', '2019-03-18'))
        self.assertTrue(self.match_date('2019-03-18', 'next week', '2019-03-25'))
        self.assertTrue(self.match_date('2019-03-29', 'next week', '2019-04-01'))

    def test_get_date_when_next_month(self):
        self.assertTrue(self.match_date('2019-07-02', 'next month', '2019-08-01'))
        self.assertTrue(self.match_date('2019-12-02', 'next month', '2020-01-01'))

    def test_get_date_when_every_day(self):
        self.date_generator.current_day = Day(self.march1)
        due_date_list = self.date_generator.get_due_dates("every day")
        self.assertTrue(len(due_date_list) == 62)

    def test_get_date_count_when_every_weekday(self):
        self.vars.recurring_month_limit = 2
        day_count = self.get_date_count('2019-03-01', 'every weekday')
        self.assertTrue(day_count == 44)

    def test_get_date_when_every_weekday(self):
        self.vars.recurring_month_limit = 2
        self.date_generator.current_day = Day(self.march1)
        due_date_list = self.date_generator.get_due_dates("every weekday")
        self.assertTrue(len(due_date_list) == 44)
        self.assertTrue(due_date_list[0].date_string == "2019-03-01")
        self.assertTrue(due_date_list[1].date_string == "2019-03-04")
        self.assertTrue(due_date_list[2].date_string == "2019-03-05")
        self.assertTrue(due_date_list[3].date_string == "2019-03-06")
        self.assertTrue(due_date_list[4].date_string == "2019-03-07")

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
        self.assertTrue(self.get_date_count('2019-03-01', 'every w') == 9)

    def test_get_date_when_every_thursday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every th') == 8)

    def test_get_date_when_every_friday(self):
        self.vars.recurring_month_limit = 2
        day_count = self.get_date_count('2019-03-01', 'every f')
        self.assertTrue(day_count == 9)

    def test_get_date_when_every_saturday(self):
        self.vars.recurring_month_limit = 2
        self.assertTrue(self.get_date_count('2019-03-01', 'every sa') == 9)

    def test_short_date(self):
        due_date_list = self.date_generator.get_due_dates("apr 14")
        self.assertTrue(len(due_date_list) == 1)
        self.assertTrue(due_date_list[0].date_string == '2021-04-14')

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

    def test_get_due_date(self):
        due_date = self.date_generator.get_due_date("this week")
        self.assertTrue(len(due_date.date_string) == 0)
        due_date = self.date_generator.get_due_date("sep 24")
        self.assertIn("09-24", due_date.date_string)


if __name__ == "__main__":
    unittest.main()
