import unittest

from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.task import Task
from taskmgr.lib.task_sync import Importer, SyncAction
from taskmgr.lib.tasks import Tasks
from tests.mock_tasks_service import MockTasksService


class TestSyncImporter(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.db = JsonFileDatabase(db_name="test_sync_importer_test_db")
        self.tasks = Tasks(self.db)
        self.importer = Importer(self.service, self.tasks)

    def tearDown(self):
        self.db.remove()
        self.tasks.clear()

    def test_convert_datetime(self):
        date_string = self.importer.convert_rfc3339_to_date_string("2019-05-25T00:00:00.000Z")
        self.assertEqual(date_string, '2019-05-25')

    def test_pull_tasks_from_service_when_empty(self):
        self.service.return_empty_tasks = True
        task_list = self.importer.convert()
        self.assertListEqual(task_list, [])

    def test_pull_tasks_from_service_when_null(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': '', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.importer.convert()
        self.assertListEqual(task_list, [])

    def test_title_to_text(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': ''}]}
        task_list = self.importer.convert()
        self.assertTrue(len(task_list) == 2)
        task1 = task_list[0]
        self.assertTrue(task1.text == "Title1")

    def test_deleted_to_deleted(self):
        self.service.tasks = {'kind': 'tasks#tasks', 'etag': '', 'items': [
            {'kind': 'tasks#task', 'id': '', 'title': 'Title1', 'updated': '',
             'position': '', 'status': '', 'due': '', 'deleted': True}]}
        task_list = self.importer.convert()
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
        task_list = self.importer.convert()
        self.assertTrue(len(task_list) == 2)
        task1 = task_list[0]
        self.assertTrue(task1.label == "Notes1")

    def test_import_tasks(self):

        task100 = Task('Task100')
        task100.external_id = "100"

        task101 = Task('Task101')
        task101.external_id = "100"
        task101.label = "home"
        task101.deleted = False

        task102 = Task('Task101')
        task102.deleted = True
        task102.external_id = "100"

        tasks_list = [task100, task101, task102]

        sync_results = self.importer.import_tasks(tasks_list)
        sync_results_list = sync_results.get_list()
        self.assertTrue(len(sync_results_list) == 3)

        self.assertTrue(sync_results_list[0] == SyncAction.ADDED)
        self.assertTrue(sync_results_list[1] == SyncAction.UPDATED)
        self.assertTrue(sync_results_list[2] == SyncAction.DELETED)




