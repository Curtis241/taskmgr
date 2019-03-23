import unittest

from taskmgr.lib.client_lib import CliClient
from taskmgr.lib.database import Database
from taskmgr.lib.tasks import SortType


class TestingFileDatabase(Database):

    def __init__(self):
        super().__init__()
        self.remove()

    def get_db_path(self):
        return self.make_db_path("test_tasks_db")


class TestCliClient(unittest.TestCase):

    def setUp(self):
        self.client = CliClient(TestingFileDatabase())
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tommorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "next m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "next sa")
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
        tasks = self.client.list_tasks()
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_list_tasks_by_label(self):
        tasks = self.client.list_tasks(SortType.Label)
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_list_tasks_by_project(self):
        tasks = self.client.list_tasks(SortType.Project)
        self.assertTrue(len(tasks.get_list()) == 9)

    def test_encoding_decoding_date_string(self):
        from datetime import datetime
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        print(date_string)
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)


if __name__ == "__main__":
    unittest.main()
