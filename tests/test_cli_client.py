import unittest
from datetime import datetime, timedelta

from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.presenter.date_generator import DateGenerator

from taskmgr.lib.presenter.file_exporter import FileExporter
from taskmgr.lib.view.cli_client import CliClient
from taskmgr.lib.variables import CommonVariables


class MockFileExporter(FileExporter):

    def save(self, table_row_list, output_dir) -> str: pass


class TestCliClient(unittest.TestCase):

    def setUp(self):
        variables = CommonVariables('test_variables.ini')
        mgr = DatabaseManager(variables)

        self.tasks = mgr.get_tasks_model()
        self.client = CliClient(mgr, MockFileExporter())
        self.client.remove_all_tasks()
        self.date_generator = DateGenerator()

    def tearDown(self):
        self.client.remove_all_tasks()

    def test_add_task(self):
        self.client.add_task("Clean garage", "", "home", "empty")
        self.client.display_all_tasks()
        row_count = len(self.client.task_table.get_table())
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
        rows = self.client.display_all_tasks()
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
        rows = self.client.group_by_label()
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
        rows = self.client.group_by_project()
        self.assertTrue(len(rows) == 9)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        task = self.client.edit_task(1, "text_value", "", "all", "apr 14")
        self.assertEqual(task.text, 'text_value')
        self.assertEqual(task.label, "all")
        self.assertEqual(task.deleted, False)
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.project, 'home')
        self.assertEqual(task.date_expression, 'apr 14')
        self.assertEqual(task.due_date.date_string, '2020-04-14')
        self.assertEqual(task.due_date.completed, False)

    def test_reschedule_tasks(self):
        today = Today()
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        self.client.add_task("Book flight to New York", "@at_computer", "work", "m")
        self.client.add_task("Repair deck", "@waiting_on", "home", "sa")
        self.client.add_task("Call friend for birthday", "@call", "home", "m")
        self.client.add_task("Paint picture", "@idea", "home", "sa")
        self.client.add_task("Build puzzle with family", "@idea", "home", "su")
        self.client.add_task("Schedule meeting with SW team", "@meeting", "work", "m")
        self.client.add_task("Create facebook 2.0 app", "@idea", "", "empty")
        task_list = self.client.display_all_tasks()
        self.assertTrue(len(task_list) > 0)
        task1 = task_list[0]
        self.assertIsNotNone(task1)
        self.assertTrue(task1.due_date.date_string == today.to_date_string())

        future_day = today.to_date_time() + timedelta(days=1)
        future_day = Day(future_day)
        self.client.reschedule_tasks(future_day)

        task_list = self.client.display_all_tasks()
        self.assertTrue(len(task_list) > 0)
        task1 = task_list[0]
        self.assertIsNotNone(task1)
        self.assertTrue(task1.due_date.date_string == future_day.to_date_string())

    def test_today(self):
        self.client.add_task("task1", "home", "home", "empty")
        self.client.add_task("task2", "home", "home", "today")
        rows = self.client.filter_by_today()
        self.assertTrue(len(list(rows)) == 1)

    def test_delete(self):
        self.client.add_task("Clean car", "@waiting_on", "home", "today")
        self.client.add_task("Clean bathroom", "", "home", "tomorrow")
        task_list = self.client.delete_tasks_by_index((1, 2,))
        self.assertTrue(len(task_list) == 2)
        self.assertTrue(task_list[0].deleted)
        self.assertTrue(task_list[1].deleted)

    def test_complete(self):
        due_dates = self.date_generator.get_due_dates("every m")
        task_list = self.client.add_task("task1", "home", "home", "every m")
        for task in task_list:
            self.client.complete_tasks((task.index,))

        rows = self.client.display_all_tasks()
        self.assertTrue(len(due_dates) == len(rows))

        done_list = [row.due_date.completed for row in rows]
        self.assertIsNotNone(done_list)
        self.assertTrue("False" not in done_list)

    def test_count(self):
        summary_list = self.client.count_all_tasks()
        self.assertIsNotNone(summary_list)


