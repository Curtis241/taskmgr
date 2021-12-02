import unittest
from datetime import datetime, timedelta

from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient


class MockFileManager(FileManager):

    @staticmethod
    def save_tasks(task_list): pass

    @staticmethod
    def open_tasks(path) -> list: pass

    @staticmethod
    def save_snapshots(snapshot_list): pass


class TestCliClient(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables('test_variables.ini')
        mgr = DatabaseManager(self.vars)

        self.tasks = mgr.get_tasks_model()
        self.client = CliClient(mgr, MockFileManager())
        self.client.remove_all_tasks()
        self.date_generator = DateGenerator()

        self.june4 = Day(datetime.strptime("2021-06-04", self.vars.date_format))
        self.june7 = Day(datetime.strptime("2021-06-07", self.vars.date_format))
        self.june9 = Day(datetime.strptime("2021-06-09", self.vars.date_format))

    def tearDown(self):
        self.client.remove_all_tasks()

    def test_add_task(self):
        self.client.add_task("Clean garage", "", "home", "empty")
        self.client.list_all_tasks()
        row_count = len(self.client.task_table.get_table().rows)
        self.assertTrue(row_count == 1)

    def test_list_all_tasks(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.client.add_task("Create facebook 2.0 app", "@idea", "", "empty")
        rows = self.client.list_all_tasks()
        self.assertTrue(len(rows) == 9)

    def test_list_tasks_by_label(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.client.add_task("Create facebook 2.0 app", "@idea", "", "empty")
        rows = self.client.group_tasks_by_label()
        self.assertTrue(len(rows) == 9)

    def test_list_tasks_by_project(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.client.add_task("Create facebook 2.0 app", "@idea", "", "empty")
        rows = self.client.group_tasks_by_project()
        self.assertTrue(len(rows) == 9)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task_using_all_fields(self):
        self.client.add_task("Clean car", "deprecated", "home", "today")
        task_list = self.client.edit_task(1, "text_value", "current", "work", "apr 14")
        self.assertTrue(len(task_list) == 1)
        task = task_list[0]
        self.assertEqual(task.text, 'text_value')
        self.assertEqual(task.label, "current")
        self.assertEqual(task.deleted, False)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.project, 'work')
        self.assertEqual(task.date_expression, 'apr 14')
        self.assertEqual(task.due_date.date_string, '2021-04-14')
        self.assertEqual(task.due_date.completed, False)

    def test_today(self):
        self.client.add_task("task1", "home", "home", "empty")
        self.client.add_task("task2", "home", "home", "today")
        rows = self.client.filter_tasks_by_today()
        self.assertTrue(len(list(rows)) == 1)

    def test_delete(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        task_list = self.client.delete_tasks((1, 2,))
        self.assertTrue(len(task_list) == 2)
        self.assertTrue(task_list[0].deleted)
        self.assertTrue(task_list[1].deleted)

    def test_complete(self):
        due_dates = self.date_generator.get_due_dates("every m")
        task_list = self.client.add_task("task1", "home", "home", "every m")
        for task in task_list:
            self.client.complete_tasks((task.index,))

        rows = self.client.list_all_tasks()
        self.assertTrue(len(due_dates) == len(rows))

        done_list = [row.due_date.completed for row in rows]
        self.assertIsNotNone(done_list)
        self.assertTrue("False" not in done_list)

    def test_count_all_tasks(self):
        self.tasks.add("task1", "label1", "project1", "today")
        snapshot_list = self.client.count_all_tasks()
        self.assertIsNotNone(snapshot_list)
        self.assertTrue(len(snapshot_list) == 1)

    def test_count_by_date(self):
        self.tasks.add("task1", "label1", "project1", "today")
        date_string = Today().to_date_string()
        snapshot_list = self.client.count_tasks_by_due_date(date_string)
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.count == 1)

    def test_count_by_due_date_range(self):
        june4_date_string = self.june4.to_date_string()
        june9_date_string = self.june9.to_date_string()
        self.tasks.add("task1", "current", "work", june4_date_string)
        self.tasks.add("task2", "current", "work", self.june7.to_date_string())
        self.tasks.add("task3", "current", "work", june9_date_string)
        snapshot_list = self.client.count_tasks_by_due_date_range(june4_date_string, june9_date_string)
        self.assertTrue(len(snapshot_list) == 1)

    def test_count_by_project(self):
        date_string = Today().to_date_string()
        self.tasks.add("task1", "current", "work", date_string)
        self.tasks.add("task2", "current", "work", date_string)
        self.tasks.add("task3", "current", "work", date_string)
        snapshot_list = self.client.count_tasks_by_project("work")
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.count == 3)



