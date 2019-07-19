import unittest

from taskmgr.lib.client_lib import SyncClient, ImportObject
from taskmgr.lib.database import YamlFileDatabase, JsonFileDatabase
from taskmgr.lib.date_generator import DueDate
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import Tasks
from tests.mock_tasks_service import MockTasksService


class TestSyncClient(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.db = JsonFileDatabase(db_name="test_sync_client_test_db")
        self.tasks = Tasks(self.db)
        self.sync_client = SyncClient(self.service, self.tasks)

    def tearDown(self):
        self.db.remove()
        self.tasks.clear()

    def test_convert_datetime(self):
        date_string = self.sync_client.convert_rfc3339_to_date_string("2019-05-25T00:00:00.000Z")
        self.assertEqual(date_string, '2019-05-25')

    def test_pull_tasks_from_service_when_empty(self):
        self.service.return_empty_tasks = True
        task_list = self.sync_client.pull_tasks_from_service()
        self.assertListEqual(task_list, [])

    def test_pull_tasks_from_service_when_null(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': '', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.sync_client.pull_tasks_from_service()
        self.assertListEqual(task_list, [])

    def test_title_to_text(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.sync_client.pull_tasks_from_service()
        self.assertTrue(len(task_list) == 2)
        task1 = task_list[0]
        self.assertTrue(task1.text == "Title1")

    def test_deleted_to_deleted(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': '', 'deleted': True}]}
        task_list = self.sync_client.pull_tasks_from_service()
        self.assertTrue(len(task_list) == 2)
        task1 = task_list[0]
        self.assertTrue(task1.deleted)

    def test_notes_to_label(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4OTU3OTc2NTQ1OTMxNjU1',
             'title': 'Task4',
             'updated': '2019-05-17T03:48:30.000Z',
             'position': '00000000000000000001', 'notes': 'Notes1',
             'status': 'needsAction'}]}
        task_list = self.sync_client.pull_tasks_from_service()
        self.assertTrue(len(task_list) == 2)
        task1 = task_list[0]
        self.assertTrue(task1.label == "Notes1")

    def test_import_tasks(self):

        task100 = Task('Task100')
        task100.external_id = "100"

        task101 = Task('Task101')
        task101.external_id = "100"

        task102 = Task('Task101')
        task102.deleted = True
        task102.external_id = "100"

        tasks_list = [task100, task101, task102]

        import_results = self.sync_client.import_tasks(tasks_list)
        import_results_list = import_results.get_list()
        self.assertTrue(len(import_results_list) == 3)

        result1 = import_results_list[0]
        print(f"result1: {dict(result1)}")
        self.assertTrue(result1.action == ImportObject.ADDED)
        self.assertTrue(len(result1.task.id) > 0)

        result2 = import_results_list[1]
        print(f"result2: {dict(result2)}")
        self.assertTrue(result2.action == ImportObject.UPDATED)
        self.assertFalse(result2.task.deleted)

        result3 = import_results_list[2]
        print(f"result3: {dict(result3)}")
        self.assertTrue(result3.action == ImportObject.DELETED)
        self.assertTrue(result3.task.deleted)

    def test_export_tasks(self):
        task100 = Task('Task100')
        task100.project = "home"
        due_date = DueDate()
        due_date.completed = False
        due_date.date_string = '2019-04-17'
        task100.due_dates = [due_date]

        task101 = Task('Task101')
        task101.project = "home"

        task102 = Task('Task102')
        task102.project = "work"

        tasks_list = [task100, task101, task102]
        gtasks_list = self.sync_client.export_tasks(tasks_list)
        self.assertTrue(len(gtasks_list) == 2)


