import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.task_sync import CsvFileImporter, SyncAction
from taskmgr.lib.presenter.tasks import Tasks


class TestCsvFileImporter(unittest.TestCase):

    def setUp(self):
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.tasks = Tasks(self.db)
        self.importer = CsvFileImporter(self.tasks)

    def tearDown(self):
        self.db.clear()

    def test_convert_tasks(self):
        obj_list = list()
        obj_list.append({'index': '1', 'done': 'True', 'text': 'task1', 'project': 'tmp', 'label': 'current',
                 'due_date': '2020-09-10', 'last_updated': '2020-09-10 22:37:23', 'deleted': 'False',
                 'unique_id': 'bc2d81c94e3844228ccb9bfe2613c089'})
        obj_list.append({'index': '2', 'done': 'False', 'text': 'task2', 'project': 'tmp', 'label': 'current',
                 'due_date': '2020-10-06', 'last_updated': '2020-10-06 22:00:46', 'deleted': 'False',
                 'unique_id': '3413035ab1f14cccb70a315e42c3242e'})
        obj_list.append({'index': '3', 'done': 'False', 'text': 'task3', 'project': 'tmp', 'label': 'current',
                 'due_date': '2020-10-06', 'last_updated': '2020-10-06 22:01:05', 'deleted': 'False',
                 'unique_id': '1fd2878c4c64446fbbce21b79a7ce1ca'})
        task_list = self.importer.convert(obj_list)
        self.assertTrue(len(task_list) == 3)


    def test_import_tasks(self):
        task100 = Task('Task100')
        task100.label = "added"
        task100.unique_id = "1"

        task101 = Task('Task100')
        task101.label = "updated"
        task101.deleted = False
        task101.unique_id = "1"

        task102 = Task('Task100')
        task102.deleted = True
        task102.label = "deleted"
        task102.unique_id = "1"

        tasks_list = [task100, task101, task102]

        sync_results = self.importer.import_tasks(tasks_list)
        sync_results_list = sync_results.get_list()
        self.assertTrue(len(sync_results_list) == 3)

        print(sync_results_list)
        self.assertTrue(sync_results_list[0] == SyncAction.ADDED)
        self.assertTrue(sync_results_list[1] == SyncAction.UPDATED)
        self.assertTrue(sync_results_list[2] == SyncAction.DELETED)
