from datetime import datetime
import unittest
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.date_generator import DateGenerator, Day, DateParser, Today, DayOfWeekHandler


class TestDateGenerator(unittest.TestCase):

    def setUp(self):
        self.march1 = datetime.strptime('2019-03-01', CommonVariables.date_format)

    def tearDown(self): pass

    def test_get_weekday_number(self):
        parser = DateParser("none", Day(datetime.now()))
        self.assertIsNone(parser.get_weekday_number("today"))
        self.assertTrue(parser.get_weekday_number("m") == 0)

    def test_pad_number(self):
        current_date_time = datetime.strptime('2019-03-12', CommonVariables.date_format)
        day = Day(current_date_time)
        date_list = day.to_date_list()
        self.assertListEqual(date_list, ['2019-03-12'])

    def test_get_date_when_in_same_week(self):
        current_date_time = datetime.strptime('2019-03-12', CommonVariables.date_format)
        generator = DateGenerator("w", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-03-13'])

    def test_get_date_when_in_next_week(self):
        current_date_time = datetime.strptime('2019-03-12', CommonVariables.date_format)
        generator = DateGenerator("m", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-03-18'])

    def test_get_date_when_in_next_month(self):
        current_date_time = datetime.strptime('2019-03-29', CommonVariables.date_format)
        generator = DateGenerator("tu", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-04-02'])

    def test_get_date_when_today(self):
        day = Day(datetime.now())
        generator = DateGenerator("today", day)
        date_list = generator.get_dates()
        self.assertListEqual(date_list, day.to_date_list())

    def test_get_date_when_tomorrow(self):
        current_date_time = datetime.strptime('2019-03-29', CommonVariables.date_format)
        generator = DateGenerator("tomorrow", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-03-30'])

    def test_get_date_when_next_week(self):
        current_date_time = datetime.strptime('2019-03-17', CommonVariables.date_format)
        generator = DateGenerator("next week", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-03-18'])

        current_date_time = datetime.strptime('2019-03-18', CommonVariables.date_format)
        generator = DateGenerator("next week", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-03-25'])

        current_date_time = datetime.strptime('2019-03-29', CommonVariables.date_format)
        generator = DateGenerator("next week", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-04-01'])

    def test_get_data_when_next_month(self):
        current_date_time = datetime.strptime('2019-07-02', CommonVariables.date_format)
        generator = DateGenerator("next month", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2019-08-05'])

        current_date_time = datetime.strptime('2019-12-02', CommonVariables.date_format)
        generator = DateGenerator("next month", Day(current_date_time))
        date_list = generator.get_dates()
        self.assertListEqual(date_list, ['2020-01-06'])

    def test_get_data_when_every_day(self):
        generator = DateGenerator("every day", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 30)

    def test_get_data_when_every_weekday(self):
        generator = DateGenerator("every weekday", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 20)

    def test_get_data_when_every_sunday(self):
        generator = DateGenerator("every su", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 5)

    def test_get_data_when_every_monday(self):
        generator = DateGenerator("every m", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 4)

    def test_get_data_when_every_tuesday(self):
        generator = DateGenerator("every tu", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 4)

    def test_get_data_when_every_wednesday(self):
        generator = DateGenerator("every w", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 4)

    def test_get_data_when_every_thursday(self):
        generator = DateGenerator("every th", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 4)

    def test_get_data_when_every_friday(self):
        generator = DateGenerator("every f", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 4)

    def test_get_data_when_every_saturday(self):
        generator = DateGenerator("every sa", Day(self.march1))
        date_list = generator.get_dates()
        self.assertTrue(len(date_list) == 5)

    def test_get_week_count(self):
        self.assertTrue(DateParser.get_week_count(3, 2019) == 5)


if __name__ == "__main__":
    unittest.main()
