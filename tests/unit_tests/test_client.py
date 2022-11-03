import unittest
from datetime import datetime

from pydantic.error_wrappers import ValidationError

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.client import Client
from taskmgr.lib.view.client_args import *


class UnitTestClient(Client):
    logger = AppLogger("unit_test_client").get_logger()

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, task_list: list):
        return task_list

    def display_snapshots(self, snapshot_list: list):
        return snapshot_list

    def display_due_date_error(self, message: str):
        self.logger.info(message)

    def display_invalid_index_error(self, index: int):
        self.logger.info(f"Provided index {index} is invalid")


class TestClient(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables('test_variables.ini')

        mgr = DatabaseManager(self.vars)
        self.client = UnitTestClient(mgr)
        self.client.remove_all_tasks()
        # self.tasks = mgr.get_tasks_model()
        self.date_generator = DateGenerator()

        self.june3 = Day(datetime.strptime("2021-06-03", self.vars.date_format))
        self.june4 = Day(datetime.strptime("2021-06-04", self.vars.date_format))
        self.june7 = Day(datetime.strptime("2021-06-07", self.vars.date_format))
        self.june9 = Day(datetime.strptime("2021-06-09", self.vars.date_format))

    def tearDown(self):
        self.client.remove_all_tasks()

    def test_add_task(self):
        self.client.add(AddArgs(name="Clean garage", label="", project="home", due_date="today"))
        task_list = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertEqual(len(task_list), 1)

    def test_list_all_tasks(self):
        self.client.add(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        self.client.add(AddArgs(name="Book flight to New York", label="@at_computer", project="work", due_date="m"))
        self.client.add(AddArgs(name="Repair deck", label="@waiting_on", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Call friend for birthday", label="@call", project="home", due_date="m"))
        self.client.add(AddArgs(name="Paint picture", label="@idea", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Build puzzle with family", label="@idea", project="home", due_date="su"))
        self.client.add(AddArgs(name="Schedule meeting with SW team", label="@meeting", project="work", due_date="m"))
        self.client.add(AddArgs(name="Create facebook 2.0 app", label="@idea", project="", due_date="today"))
        task_list = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertTrue(len(task_list) == 9)

    def test_list_tasks_by_label(self):
        self.client.add(AddArgs(name="Clean car", label="waiting_on", project="home", due_date="today"))
        self.client.add(AddArgs(name="Clean bathroom", label="idea", project="home", due_date="tomorrow"))
        self.client.add(AddArgs(name="Book flight to New York", label="at_computer", project="work", due_date="m"))
        self.client.add(AddArgs(name="Repair deck", label="waiting_on", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Call friend for birthday", label="call", project="home", due_date="m"))
        self.client.add(AddArgs(name="Paint picture", label="idea", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Build puzzle with family", label="idea", project="home", due_date="su"))
        self.client.add(AddArgs(name="Schedule meeting with SW team", label="meeting", project="work", due_date="m"))
        self.client.add(AddArgs(name="Create facebook 2.0 app", label="idea", project="work", due_date="today"))
        task_list = self.client.group_tasks_by_label()
        self.assertTrue(len(task_list) == 9)

    def test_list_tasks_by_project(self):
        self.client.add(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        self.client.add(AddArgs(name="Book flight to New York", label="@at_computer", project="work", due_date="m"))
        self.client.add(AddArgs(name="Repair deck", label="@waiting_on", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Call friend for birthday", label="@call", project="home", due_date="m"))
        self.client.add(AddArgs(name="Paint picture", label="@idea", project="home", due_date="sa"))
        self.client.add(AddArgs(name="Build puzzle with family", label="@idea", project="home", due_date="su"))
        self.client.add(AddArgs(name="Schedule meeting with SW team", label="@meeting", project="work", due_date="m"))
        self.client.add(AddArgs(name="Create facebook 2.0 app", label="@idea", project="work", due_date="today"))
        task_list = self.client.group_tasks_by_project()
        self.assertTrue(len(task_list) == 9)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task_using_all_fields(self):
        task_list = self.client.add(AddArgs(name="Clean car", label="deprecated", project="home", due_date="today"))
        self.assertTrue(len(task_list) == 1)
        task = task_list[0]

        args = EditArgs(index=task.index, name="New Text", label="current", project="work", due_date="apr 14")
        task_list = self.client.edit(args)
        task = task_list[0]

        self.assertEqual(task.name, 'New Text')
        self.assertEqual(task.label, "current")
        self.assertEqual(task.deleted, False)
        self.assertEqual(task.project, 'work')
        self.assertEqual(task.due_date, '2022-04-14')
        self.assertEqual(task.completed, False)

    def test_today(self):
        self.client.add(AddArgs(name="task1", label="home", project="home", due_date="empty"))
        self.client.add(AddArgs(name="task2", label="home", project="home", due_date="today"))
        task_list = self.client.filter_tasks_by_today()
        self.assertTrue(len(task_list) == 1)

    def test_delete(self):
        self.client.add(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        task_list = self.client.delete(DeleteArgs(indexes=(1, 2,)))
        self.assertTrue(len(task_list) == 2)
        self.assertTrue(task_list[0].deleted)
        self.assertTrue(task_list[1].deleted)

    def test_complete(self):
        due_dates = self.date_generator.get_due_dates("every m")
        task_list = self.client.add(AddArgs(name="task1", label="home", project="home", due_date="every m"))
        for task in task_list:
            self.client.complete(CompleteArgs(indexes=(task.index,), time_spent=0))
        rows = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertTrue(len(due_dates) == len(rows))

        done_list = [row.completed for row in rows]
        self.assertIsNotNone(done_list)
        self.assertTrue("False" not in done_list)

    def test_count_all_tasks(self):
        self.client.add(AddArgs(name="task1", label="label1", project="project1", due_date="today"))
        snapshot_list = self.client.count_all_tasks()
        self.assertIsNotNone(snapshot_list)
        self.assertTrue(len(snapshot_list) == 1)

    def test_count_by_date(self):
        self.client.add(AddArgs(name="task1", label="label1", project="project1", due_date="today"))
        args = DueDateArgs(due_date=Today().to_date_string())
        snapshot_list = self.client.count_tasks_by_due_date(args)
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 1)

    def test_count_by_due_date_range(self):
        june4_date_string = self.june4.to_date_string()
        june9_date_string = self.june9.to_date_string()
        self.client.add(AddArgs(name="task1", label="current", project="work", due_date=self.june3.to_date_string()))
        self.client.add(AddArgs(name="task2", label="current", project="work", due_date=june4_date_string))
        self.client.add(AddArgs(name="task3", label="current", project="work", due_date=june9_date_string))
        args = DueDateRangeArgs(min_date=june4_date_string, max_date=june9_date_string)
        snapshot_list = self.client.count_tasks_by_due_date_range(args)
        self.assertTrue(len(snapshot_list) == 2)

    def test_count_by_project(self):
        date_string = Today().to_date_string()
        self.client.add(AddArgs(name="task1", label="current", project="work", due_date=date_string))
        self.client.add(AddArgs(name="task2", label="current", project="work", due_date=date_string))
        self.client.add(AddArgs(name="task3", label="current", project="work", due_date=date_string))
        snapshot_list = self.client.count_tasks_by_project(ProjectArgs(project="work", page=0))
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 3)

    def test_count_by_project_with_incorrect_value(self):
        self.client.add(AddArgs(name="task1", label="current", project="work", due_date="today"))
        snapshot_list = self.client.count_tasks_by_project(ProjectArgs(project="work2", page=0))
        self.assertTrue(len(snapshot_list) == 0)
