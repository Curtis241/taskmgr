import unittest
from datetime import datetime, timedelta
from taskmgr.lib.client_lib import CliClient
from taskmgr.lib.date_generator import Day, Today
from taskmgr.lib.tasks import SortType
from tests.file_test_database import FileTestDatabase


class TestCliClient(unittest.TestCase):

    def setUp(self):
        self.client = CliClient(FileTestDatabase())
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.client.add_task("Create facebook 2.0 app", "@idea", "", "")

    def tearDown(self):
        self.client.remove_tasks()

    def test_add_task(self):
        tasks = self.client.add_task("Clean garage", "", "home", "")
        self.assertTrue(len(tasks.get_list()) == 10)

    def test_list_all_tasks(self):
        tasks = self.client.group_tasks()
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_list_tasks_by_label(self):
        tasks = self.client.group_tasks(SortType.Label)
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_list_tasks_by_project(self):
        tasks = self.client.group_tasks(SortType.Project)
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_list_tasks_by_date(self):
        tasks = self.client.filter_tasks(SortType.DueDate)
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task(self):
        kwargs = {"index": 1, "text": "text_value", "label": None, "project": None, "date_expression": "apr 14"}
        task = self.client.edit_task(**kwargs)
        self.assertDictEqual(dict(task),
                             {'index': 1, 'text': 'text_value', 'label': '@waiting_on', 'deleted': False, 'priority': 1,
                              'project': 'home', 'date_expression': 'apr 14',
                              'due_dates': [{'date_string': '2019-04-14', 'completed': False}]}
                             )

    def test_reschedule_tasks(self):
        today = Today()
        tasks = self.client.group_tasks()
        self.assertTrue(len(tasks.get_list()) == 9)
        task = tasks.get_task_by_index(9)
        self.assertTrue(len(task.due_dates) == 1)
        self.assertTrue(task.due_dates[0].date_string == today.to_date_string())

        future_day = today.to_date_time() + timedelta(days=1)
        future_day = Day(future_day)
        self.client.reschedule_tasks(future_day)

        tasks = self.client.group_tasks()
        self.assertTrue(len(tasks.get_list()) == 9)
        task = tasks.get_task_by_index(9)
        self.assertTrue(len(task.due_dates) == 1)
        self.assertTrue(task.due_dates[0].date_string == future_day.to_date_string())

if __name__ == "__main__":
    unittest.main()
