import unittest
from datetime import datetime

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.client import Client
from taskmgr.lib.view.client_args import *


class UnitTestClient(Client):

    logger = AppLogger("unit_test_client").get_logger()

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_attribute_error(self, param: str, message: str):
        pass

    def display_tasks(self, result: QueryResult):
        return result.to_list()

    def display_snapshots(self, result: QueryResult):
        return result.to_list()

    def display_time_cards(self, result: QueryResult):
        pass

    def display_due_date_error(self, message: str):
        self.logger.info(message)

    def display_invalid_index_error(self, index: int):
        self.logger.info(f"Provided index {index} is invalid")


class TestClient(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables('test_variables.ini')
        self.vars.redis_host = "localhost"

        mgr = DatabaseManager(self.vars)
        self.client = UnitTestClient(mgr)
        self.client.remove_all_tasks()
        # self.tasks = mgr.get_tasks_model()
        self.date_generator = DateTimeGenerator()

        self.june3 = Day(datetime.strptime("2021-06-03", self.vars.date_format))
        self.june4 = Day(datetime.strptime("2021-06-04", self.vars.date_format))
        self.june7 = Day(datetime.strptime("2021-06-07", self.vars.date_format))
        self.june9 = Day(datetime.strptime("2021-06-09", self.vars.date_format))

    def tearDown(self):
        self.client.remove_all_tasks()

    def test_add_task(self):
        self.client.add_task(AddArgs(name="Clean garage", label="", project="home", due_date="today"))
        task_list = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertEqual(len(task_list), 1)

    def test_list_all_tasks(self):
        self.client.add_task(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add_task(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        self.client.add_task(AddArgs(name="Book flight to New York", label="@at_computer", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Repair deck", label="@waiting_on", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Call friend for birthday", label="@call", project="home", due_date="m"))
        self.client.add_task(AddArgs(name="Paint picture", label="@idea", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Build puzzle with family", label="@idea", project="home", due_date="su"))
        self.client.add_task(AddArgs(name="Schedule meeting with SW team", label="@meeting", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Create facebook 2.0 app", label="@idea", project="", due_date="today"))
        task_list = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertTrue(len(task_list) == 9)

    def test_list_tasks_by_label(self):
        self.client.add_task(AddArgs(name="Clean car", label="waiting_on", project="home", due_date="today"))
        self.client.add_task(AddArgs(name="Clean bathroom", label="idea", project="home", due_date="tomorrow"))
        self.client.add_task(AddArgs(name="Book flight to New York", label="at_computer", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Repair deck", label="waiting_on", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Call friend for birthday", label="call", project="home", due_date="m"))
        self.client.add_task(AddArgs(name="Paint picture", label="idea", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Build puzzle with family", label="idea", project="home", due_date="su"))
        self.client.add_task(AddArgs(name="Schedule meeting with SW team", label="meeting", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Create facebook 2.0 app", label="idea", project="work", due_date="today"))
        task_list = self.client.group_tasks_by_label()
        self.assertTrue(len(task_list) == 9)

    def test_list_tasks_by_project(self):
        self.client.add_task(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add_task(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        self.client.add_task(AddArgs(name="Book flight to New York", label="@at_computer", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Repair deck", label="@waiting_on", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Call friend for birthday", label="@call", project="home", due_date="m"))
        self.client.add_task(AddArgs(name="Paint picture", label="@idea", project="home", due_date="sa"))
        self.client.add_task(AddArgs(name="Build puzzle with family", label="@idea", project="home", due_date="su"))
        self.client.add_task(AddArgs(name="Schedule meeting with SW team", label="@meeting", project="work", due_date="m"))
        self.client.add_task(AddArgs(name="Create facebook 2.0 app", label="@idea", project="work", due_date="today"))
        task_list = self.client.group_tasks_by_project()
        self.assertTrue(len(task_list) == 9)

    def test_encoding_decoding_date_string(self):
        now = datetime.now()
        date_string = now.strftime("%m-%d-%Y")
        date_object = datetime.strptime(date_string, "%m-%d-%Y")
        self.assertIsInstance(date_object, datetime)

    def test_edit_task_using_all_fields(self):
        task_list = self.client.add_task(AddArgs(name="Clean car", label="deprecated", project="home", due_date="today"))
        self.assertTrue(len(task_list) == 1)
        task = task_list[0]

        args = EditArgs(index=task.index, name="New Text", label="current", project="work", due_date="apr 14")
        task_list = self.client.edit_task(args)
        task = task_list[0]

        self.assertEqual(task.name, 'New Text')
        self.assertEqual(task.label, "current")
        self.assertEqual(task.deleted, False)
        self.assertEqual(task.project, 'work')
        self.assertEqual(task.due_date, '2023-04-14')
        self.assertEqual(task.completed, False)

    def test_today(self):
        self.client.add_task(AddArgs(name="task1", label="home", project="home", due_date="empty"))
        self.client.add_task(AddArgs(name="task2", label="home", project="home", due_date="today"))
        task_list = self.client.filter_tasks_by_today()
        self.assertTrue(len(task_list) == 1)

    def test_delete(self):
        self.client.add_task(AddArgs(name="Clean car", label="@waiting_on", project="home", due_date="today"))
        self.client.add_task(AddArgs(name="Clean bathroom", label="", project="home", due_date="tomorrow"))
        task_list = self.client.delete_task(DeleteArgs(indexes=(1, 2,)))
        self.assertTrue(len(task_list) == 2)
        self.assertTrue(task_list[0].deleted)
        self.assertTrue(task_list[1].deleted)

    def test_complete(self):
        days = self.date_generator.get_days("every m")
        task_list = self.client.add_task(AddArgs(name="task1", label="home", project="home", due_date="every m"))
        for task in task_list:
            self.client.complete_task(CompleteArgs(indexes=(task.index,), time_spent=0))
        rows = self.client.list_all_tasks(ListArgs(page=0, all=False))
        self.assertTrue(len(days) == len(rows))

        done_list = [row.completed for row in rows]
        self.assertIsNotNone(done_list)
        self.assertTrue("False" not in done_list)

    def test_count_all_tasks(self):
        self.client.add_task(AddArgs(name="task1", label="label1", project="project1", due_date="today"))
        snapshot_list = self.client.count_all_tasks()
        self.assertIsNotNone(snapshot_list)
        self.assertTrue(len(snapshot_list) == 1)

    def test_count_by_date(self):
        self.client.add_task(AddArgs(name="task1", label="label1", project="project1", due_date="today"))
        args = DueDateArgs(due_date=Today().to_date_string())
        snapshot_list = self.client.count_tasks_by_due_date(args)
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 1)

    def test_count_with_date_expression(self):
        self.client.add_task(AddArgs(name="task1", label="label1", project="project1", due_date="today"))
        snapshot_list = self.client.count_tasks_by_due_date(DueDateArgs(due_date="this week"))
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 1)

    def test_count_by_due_date_range(self):
        june4_date_string = self.june4.to_date_string()
        june9_date_string = self.june9.to_date_string()
        self.client.add_task(AddArgs(name="task1", label="current", project="work", due_date=self.june3.to_date_string()))
        self.client.add_task(AddArgs(name="task2", label="current", project="work", due_date=june4_date_string))
        self.client.add_task(AddArgs(name="task3", label="current", project="work", due_date=june9_date_string))
        args = DueDateRangeArgs(min_date=june4_date_string, max_date=june9_date_string)
        snapshot_list = self.client.count_tasks_by_due_date_range(args)
        self.assertTrue(len(snapshot_list) == 2)

    def test_count_by_project(self):
        date_string = Today().to_date_string()
        self.client.add_task(AddArgs(name="task1", label="current", project="work", due_date=date_string))
        self.client.add_task(AddArgs(name="task2", label="current", project="work", due_date=date_string))
        self.client.add_task(AddArgs(name="task3", label="current", project="work", due_date=date_string))
        snapshot_list = self.client.count_tasks_by_project(ProjectArgs(project="work", page=0))
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 3)

    def test_count_by_project_with_incorrect_value(self):
        self.client.add_task(AddArgs(name="task1", label="current", project="work", due_date="today"))
        snapshot_list = self.client.count_tasks_by_project(ProjectArgs(project="work2", page=0))
        self.assertTrue(len(snapshot_list) == 0)

    def test_reschedule(self):
        self.client.add_task(AddArgs(name="task1", label="current", project="work", due_date="yesterday"))
        self.client.add_task(AddArgs(name="task2", label="current", project="work", due_date="yesterday"))
        task2 = self.client.tasks.get_task_by_name("task2")
        args = CompleteArgs(indexes=(task2.index,), time_spent=0)
        self.client.complete_task(args)
        self.client.add_task(AddArgs(name="task3", label="current", project="work", due_date="yesterday"))
        self.client.reschedule_tasks()

        snapshot_list = self.client.count_tasks_by_due_date(DueDateArgs(due_date="yesterday"))
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 1)

        snapshot_list = self.client.count_tasks_by_due_date(DueDateArgs(due_date="today"))
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]
        self.assertTrue(snapshot.task_count == 2)

    def test_group_edit(self):
        self.client.add_task(AddArgs(name="task1", label="current", project="work", due_date="yesterday"))
        t1 = self.client.tasks.get_task_by_name("task1")
        self.client.add_task(AddArgs(name="task2", label="current", project="work", due_date="yesterday"))
        t2 = self.client.tasks.get_task_by_name("task2")
        args = GroupEditArgs(indexes=(t1.index, t2.index,), label="l1")

        task_list = self.client.group_edit(args)
        self.assertEqual(len(task_list), 2)
        self.assertEqual(task_list[0].label, "l1")
        self.assertEqual(task_list[1].label, "l1")






