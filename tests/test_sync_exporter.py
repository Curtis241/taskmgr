import unittest

from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.date_generator import DueDate
from taskmgr.lib.task import Task
from taskmgr.lib.task_sync import Exporter
from taskmgr.lib.tasks import Tasks
from tests.mock_tasks_service import MockTasksService


class TestSyncExporter(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.db = JsonFileDatabase(db_name="test_sync_exporter_test_db")
        self.tasks = Tasks(self.db)
        self.exporter = Exporter(self.service, self.tasks)

    def tearDown(self): pass

    def test_export_tasks(self):
        task100 = Task('Task100')
        task100.project = "home"
        due_date = DueDate()
        due_date.completed = False
        due_date.date_string = '2019-04-17'
        task100.due_dates = [due_date]
        self.tasks.add(task100)

        task101 = Task('Task101')
        task101.project = "home"
        self.tasks.add(task101)

        task102 = Task('Task102')
        task102.project = "work"
        self.tasks.add(task102)

        # tasks_list = [task100, task101, task102]
        gtasks_list = self.exporter.convert()
        self.assertTrue(len(gtasks_list) == 2)


