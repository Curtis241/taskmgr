import unittest
from datetime import datetime, timedelta

from taskmgr.lib.client_lib import CliClient
from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.date_generator import Day, Today
from taskmgr.lib.tasks import SortType, Tasks


class TestCliClient(unittest.TestCase):

    def setUp(self):
        self.db = JsonFileDatabase("test_cli_client_file_db")
        self.client = CliClient()
        self.client.tasks = Tasks(self.db)
        self.task1 = self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.task2 = self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.task3 = self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.task4 = self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.task5 = self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.task6 = self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.task7 = self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.task8 = self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.task9 = self.client.add_task("Create facebook 2.0 app", "@idea", "", "")

    def tearDown(self):
        self.client.remove_all_tasks()
        self.db.remove()

    def test_add_task(self):
        self.client.add_task("Clean garage", "", "home", "")
        self.assertTrue(len(self.client.tasks.get_list()) == 10)

    def test_list_all_tasks(self):
        rows = self.client.group_tasks()
        self.assertTrue(len(rows) == 9)

    def test_list_tasks_by_label(self):
        rows = self.client.group_tasks(SortType.Label)
        self.assertTrue(len(rows) == 9)

    def test_list_tasks_by_project(self):
        rows = self.client.group_tasks(SortType.Project)
        self.assertTrue(len(rows) == 9)

    def test_list_tasks_by_date(self):
        kwargs = {'filter': SortType.DueDate}
        rows = self.client.filter_tasks(**kwargs)
        self.assertTrue(len(rows) == 1)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task(self):
        kwargs = {"key": self.task1.key, "text": "text_value", "label": "all", "project": None, "due_date": "apr 14"}
        task = self.client.edit_task(**kwargs)
        self.assertEqual(task.key, self.task1.key)
        self.assertEqual(task.text, 'text_value')
        self.assertEqual(task.label, "all")
        self.assertEqual(task.deleted, False)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.project, 'home')
        self.assertEqual(task.date_expression, 'apr 14')
        self.assertTrue(len(task.due_dates) == 1)
        due_date = task.due_dates[0]
        self.assertEqual(due_date.date_string, '2019-04-14')
        self.assertEqual(due_date.completed, False)

    def test_reschedule_tasks(self):
        today = Today()
        rows = self.client.group_tasks()
        self.assertTrue(len(rows) == 9)
        item = self.client.tasks.get_task_by_key(self.task1.key)

        self.assertIsNotNone(item.task)
        self.assertTrue(len(item.task.due_dates) == 1)
        self.assertTrue(item.task.due_dates[0].date_string == today.to_date_string())

        future_day = today.to_date_time() + timedelta(days=1)
        future_day = Day(future_day)
        self.client.reschedule_tasks(future_day)

        rows = self.client.group_tasks()
        self.assertTrue(len(rows) == 9)
        item = self.client.tasks.get_task_by_key(self.task1.key)
        self.assertTrue(len(item.task.due_dates) == 1)
        self.assertTrue(item.task.due_dates[0].date_string == future_day.to_date_string())


if __name__ == "__main__":
    unittest.main()
