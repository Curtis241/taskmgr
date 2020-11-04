import unittest

from taskmgr.lib.presenter.gtask_project_api import GTasksProjectAPI
from taskmgr.lib.presenter.gtasks_api import GTask, GTasksAPI
from tests.unit_tests.mock_tasks_service import MockTasksService


class TestGoogleTasks(unittest.TestCase):

    def setUp(self):
        self.service = MockTasksService()
        self.tasks_list_api = GTasksProjectAPI(self.service)
        tasklist_obj = self.tasks_list_api.get("My Tasks")
        self.tasks_api = GTasksAPI(tasklist_obj.id, self.service)

    def tearDown(self): pass

    def test_list_tasklist(self):
        tasklist_obj_list = self.tasks_list_api.list()
        self.assertTrue(len(tasklist_obj_list) == 2)

    def test_get_tasklist(self):
        tasklist_obj = self.tasks_list_api.get("My Tasks")
        self.assertIsNotNone(tasklist_obj)
        self.assertTrue(tasklist_obj.title == "My Tasks")

    def test_insert_tasklist(self):
        tasklist_obj = self.tasks_list_api.insert("Work")
        self.assertIsNotNone(tasklist_obj)
        self.assertTrue(tasklist_obj.title == "Work")

    def test_delete_tasklist(self):
        self.assertTrue(self.tasks_list_api.delete("My Tasks"))

    def test_update_tasklist(self):
        self.tasks_list_api.update("My Tasks", "Work")

    def test_list_task(self):
        task_obj_list = self.tasks_api.list()
        self.assertTrue(len(task_obj_list) == 7)
        self.assertIsInstance(task_obj_list[0], GTask)

    def test_get_task(self):
        task_obj = self.tasks_api.get_by_title("Task1")
        self.assertIsNotNone(task_obj)
        self.assertTrue(task_obj.title == "Task1")

    def test_insert_task(self):
        task = GTask()
        task.title = "Task10"
        self.assertTrue(self.tasks_api.insert(task))

    def test_delete_task(self):
        self.assertTrue(self.tasks_api.delete("Task1"))

    def test_update_task(self):
        task = GTask()
        task.title = "Task1"
        task.id = "id1"
        result = self.tasks_api.update(task)
        self.assertTrue(result.title == "Task1")
