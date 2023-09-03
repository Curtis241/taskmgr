import unittest
from datetime import datetime

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.variables import CommonVariables


class TestTimeCardsDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.vars = CommonVariables('test_variables.ini')
        self.mgr = DatabaseManager(self.vars)
        self.db = self.mgr.get_time_cards_db()
        self.db.clear()
        self.vars = CommonVariables()
        self.date = "2023-04-24"

        def get_time(time_string: str):
            dt = datetime.strptime(f'{self.date} {time_string}', self.vars.date_time_format)
            return dt.timestamp()

        self.t1 = TimeCard()
        self.t1.index = 1
        self.t1.date = self.date
        self.t1.time_in = get_time("6:00:00")
        self.t1.time_out = get_time("7:30:00")
        self.t1.total = 1.5
        self.t1.unique_id = self.db.get_unique_id()

        self.t2 = TimeCard()
        self.t2.index = 2
        self.t2.date = self.date
        self.t2.time_in = get_time("8:30:00")
        self.t2.time_out = get_time("12:00:00")
        self.t2.total = 3.5
        self.t2.unique_id = self.db.get_unique_id()

        self.t3 = TimeCard()
        self.t3.index = 3
        self.t3.date = self.date
        self.t3.time_in = get_time("12:30:00")
        self.t3.time_out = get_time("14:45:00")
        self.t3.total = 2.15
        self.t3.unique_id = self.db.get_unique_id()

        self.t4 = TimeCard()
        self.t4.index = 4
        self.t4.date = self.date
        self.t4.time_in = get_time("15:30:00")
        self.t4.time_out = get_time("16:30:00")
        self.t4.total = 2
        self.t4.unique_id = self.db.get_unique_id()

    def tearDown(self) -> None:
        self.db.clear()

    def test_insert_should_create_object(self):
        self.db.append_object(self.t1)
        self.db.replace_object(self.t1)
        result = self.db.get_all()
        self.assertEqual(result.item_count, 1)

    def test_get_timecard(self):
        self.db.append_object(self.t1)
        result = self.db.get_selected("date_timestamp",
                                      self.t1.date_timestamp,
                                      self.t1.date_timestamp)
        self.assertEqual(result.item_count, 1)
        time_card_list = result.to_list()
        time_card = time_card_list[0]
        self.assertEqual(time_card.date, self.date)

    def test_get_time_cards_by_index(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        time_card = self.db.get_object("index", 2)
        self.assertIsNotNone(time_card)
        self.assertEqual(time_card.date, self.date)

    def test_get_time_cards_by_id(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        time_card = self.db.get_object("unique_id", self.t1.unique_id)
        self.assertIsNotNone(time_card)
        self.assertEqual(time_card.unique_id, self.t1.unique_id)

    def test_object_serialization(self):
        self.db.append_object(self.t1)
        result = self.db.get_all()
        self.assertTrue(result.item_count == 1)

        time_card_list = result.to_list()
        time_card = time_card_list[0]
        self.assertEqual(self.t1.date, time_card.date)
        self.assertEqual(self.t1.index, time_card.index)
        self.assertEqual(self.t1.unique_id, time_card.unique_id)
        self.assertEqual(self.t1.total, time_card.total)
        self.assertEqual(self.t1.time_in, time_card.time_in)
        self.assertEqual(self.t1.time_out, time_card.time_out)

