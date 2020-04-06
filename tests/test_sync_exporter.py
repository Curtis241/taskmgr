import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.task_sync import GoogleTasksExporter
from taskmgr.lib.presenter.tasks import Tasks
from tests.mock_tasks_service import MockTasksService


class TestSyncExporter(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.tasks = Tasks(self.db)
        self.exporter = GoogleTasksExporter(self.service, self.tasks)

    def tearDown(self):
        self.db.clear()

    def test_export_tasks(self):
        task100 = Task('Task100')
        task100.project = "home"
        due_date = DueDate()
        due_date.completed = False
        due_date.date_string = '2019-04-17'
        task100.due_dates = [due_date]
        self.tasks.append(task100)

        task101 = Task('Task101')
        task101.project = "home"
        self.tasks.append(task101)

        task102 = Task('Task102')
        task102.project = "work"
        self.tasks.append(task102)

        # tasks_list = [task100, task101, task102]
        gtasks_list = self.exporter.convert_to_gtasklist("home")
        self.assertTrue(len(gtasks_list) == 1)


