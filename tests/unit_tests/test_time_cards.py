import unittest

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.variables import CommonVariables


class TestTimeCards(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables('test_variables.ini')
        self.time_cards = DatabaseManager(self.vars).get_time_cards_model()

    def tearDown(self):
        self.time_cards.clear()

    def test_get_time_card(self):
        self.time_cards.add("8:15am", "12pm", "today")
        time_card = self.time_cards.get_time_card_by_index(1)
        self.assertIsNotNone(time_card)
        self.assertEqual(time_card.index, 1)
        self.assertEqual(time_card.time_in, "8:15")
        self.assertEqual(time_card.time_out, "12:00")
        self.assertEqual(time_card.elapsed_time, "3:45")

    def test_add_tasks(self):
        self.time_cards.add("6am", "7:30am", "today")
        self.time_cards.add("8:30am", "12pm", "today")
        self.time_cards.add("12:30pm", "2:30pm", "today")
        self.time_cards.add("3:30pm", "5:30pm", "today")
        result = self.time_cards.get_all()
        task_list = result.to_list()
        self.assertTrue(len(task_list) == 4)

    def test_edit_label_task(self):
        self.time_cards.add("6am", "7am", "today")
        original = self.time_cards.get_time_card_by_index(1)
        original, modified = self.time_cards.edit(original.index, time_out="8am")
        self.assertEqual(modified.time_out, "8:00")

    def test_get_list_by_date_expression(self):
        self.time_cards.add("14:30", "17:30", "today")
        self.time_cards.add("14:30", "17:30", "tomorrow")
        result = self.time_cards.get_time_cards_by_date("tomorrow")
        task_list = result.to_list()
        self.assertTrue(len(task_list) == 1)

    def test_add_total_time(self):
        t1 = TimeCard()
        t1.total = "4:15"
        t2 = TimeCard()
        t2.total = "3:45"
        time_card_list = [t1, t2]
        total_time = self.time_cards.sum_total_times(time_card_list)
        self.assertEqual(total_time, "8:00")

        total_time = self.time_cards.sum_total_times([])
        self.assertEqual(total_time, "0:00")


if __name__ == "__main__":
    unittest.main()
