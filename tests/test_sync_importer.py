import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, SyncAction
from taskmgr.lib.presenter.tasks import Tasks
from tests.mock_tasks_service import MockTasksService


class TestSyncImporter(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.tasks = Tasks(self.db)
        self.importer = GoogleTasksImporter(self.service, self.tasks)

    def tearDown(self):
        self.db.clear()

    def test_convert_datetime(self):
        date_string = self.importer.convert_rfc3339_to_date_string("2019-05-25T00:00:00.000Z")
        self.assertEqual(date_string, '2019-05-25')

    def test_pull_tasks_from_service_when_empty(self):
        self.service.return_empty_tasks = True
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertListEqual(task_list, [])

    def test_pull_tasks_from_service_when_null(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': '', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertListEqual(task_list, [])

    def test_title_to_text(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertTrue(len(task_list) == 1)
        task1 = task_list[0]
        self.assertTrue(task1.text == "Title1")

    def test_deleted_to_deleted(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': '', 'deleted': True}]}
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertTrue(len(task_list) == 1)
        task1 = task_list[0]
        self.assertTrue(task1.deleted)

    def test_notes_to_label(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4OTU3OTc2NTQ1OTMxNjU1',
             'title': 'Task4',
             'updated': '2019-05-17T03:48:30.000Z',
             'position': '00000000000000000001', 'notes': 'Notes1',
             'status': 'needsAction'}]}
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertTrue(len(task_list) == 1)
        task1 = task_list[0]
        self.assertTrue(task1.label == "Notes1")

    def test_convert_completed(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': 'RlhuMVpoZ0pHSDRCUE9JZw',
             'title': 'Build sidewalk',
             'parent': '0',
             'notes': '',
             'status': 'completed',
             'completed': '2019-08-11T01:56:14.000Z',
             'deleted': False, 'hidden': True}]}
        task_list = self.importer.convert_to_task_list("My Tasks")
        self.assertTrue(len(task_list) == 1)
        task1 = task_list[0]
        self.assertIsNotNone(task1.due_date)
        task1.due_date.date_string = '2019-08-11'
        self.assertTrue(task1.due_date.completed)

    def test_import_tasks(self):
        task100 = Task('Task100')
        task100.label = "added"

        task101 = Task('Task100')
        task101.label = "updated"
        task101.deleted = False

        task102 = Task('Task100')
        task102.deleted = True
        task102.label = "deleted"

        tasks_list = [task100, task101, task102]

        sync_results = self.importer.import_tasks(tasks_list)
        sync_results_list = sync_results.get_list()
        self.assertTrue(len(sync_results_list) == 3)

        print(sync_results_list)
        self.assertTrue(sync_results_list[0] == SyncAction.ADDED)
        self.assertTrue(sync_results_list[1] == SyncAction.UPDATED)
        self.assertTrue(sync_results_list[2] == SyncAction.DELETED)
