import unittest

from dpath import util
from requests.exceptions import HTTPError
from system_tests.common import Common
from system_tests.rest_api import RestApi, Tasks, Task


class TestCrudOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.api = RestApi()
        self.tasks = Tasks()
        self.task = Task()
        self.tasks.remove_all()
        self.util = Common()

    def tearDown(self) -> None: pass

    def test_add_task_with_empty_values(self):
        with self.assertRaises(HTTPError):
            self.tasks.add("", "", "", "")

    def test_add_task_with_invalid_date_expression(self):
        response = self.tasks.add("t1", "l1", "p1", "lkj;lkj;lkj;lkj")
        print(response)

    def test_add_multiple_tasks(self):
        response = self.tasks.add("task1", "project1", "label1", "today")
        self.assertTrue(self.util.verify_structure(response))

        response = self.tasks.add("task2", "project1", "label1", "today")
        self.assertTrue(self.util.verify_structure(response))

        response = self.tasks.add("task3", "project1", "label1", "today")
        self.assertTrue(self.util.verify_structure(response))

        response = self.tasks.get_all()
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 3)

    def test_get_single_task(self):
        response = self.tasks.add("single task", "project1", "label1", "today")
        self.assertTrue(self.util.verify_structure(response))

        index = util.get(response, "tasks/0/index")
        response = self.task.get_task(index)

        self.assertTrue(self.util.verify_structure(response))
        self.assertEqual(util.get(response, "tasks/0/text"), "single task")

    def test_delete_task(self):
        self.tasks.add("task1", "project1", "label1", "today")
        self.tasks.add("task2", "project1", "label1", "today")
        response = self.tasks.add("task3", "project1", "label1", "today")

        uuid = util.get(response, "tasks/0/unique_id")
        response = self.task.delete_task(uuid)
        self.assertTrue(self.util.verify_structure(response))
        is_deleted = util.get(response, "tasks/0/deleted")
        self.assertTrue(is_deleted)

        response = self.task.undelete_task(uuid)
        self.assertTrue(self.util.verify_structure(response))
        is_deleted = util.get(response, "tasks/0/deleted")
        self.assertFalse(is_deleted)

    def test_edit_task(self):
        response = self.tasks.add("task1", "project1", "label1", "today")
        self.assertTrue(self.util.verify_structure(response))

        index = util.get(response, "tasks/0/index")
        response = self.tasks.edit(index, "task1_1", "project1_1", "label1_1", "today")
        self.assertTrue(self.util.verify_structure(response))

        text = util.get(response, "tasks/0/text")
        project = util.get(response, "tasks/0/project")
        label = util.get(response, "tasks/0/label")

        self.assertTrue(text == "task1_1")
        self.assertTrue(project == "project1_1")
        self.assertTrue(label == "label1_1")





