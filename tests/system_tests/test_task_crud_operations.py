import unittest
from dpath import util

from system_tests.rest_api import RestApi, DefaultProperty, Tasks, Task


class TestApi(unittest.TestCase):

    @staticmethod
    def verify_structure(response: dict) -> bool:
        assert type(response) is dict
        return "tasks" in response

    def setUp(self) -> None:
        self.api = RestApi()
        self.default_property = DefaultProperty()
        self.tasks = Tasks()
        self.task = Task()
        self.tasks.remove_all()

    def tearDown(self) -> None: pass

    def test_add_multiple_tasks(self):
        response = self.tasks.add("task1", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        response = self.tasks.add("task2", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        response = self.tasks.add("task3", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        response = self.tasks.get_all()
        self.assertTrue(self.verify_structure(response))
        self.assertTrue(len(response["tasks"]) == 3)

    def test_get_single_task(self):
        response = self.tasks.add("single task", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        index = util.get(response, "tasks/0/index")
        response = self.task.get_task(index)

        self.assertTrue(self.verify_structure(response))
        self.assertEqual(util.get(response, "tasks/0/text"), "single task")

    def test_delete_task(self):
        response = self.tasks.add("task1", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        response = self.tasks.add("task2", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        response = self.tasks.add("task3", "project1", "label1", "today")
        self.assertTrue(self.verify_structure(response))

        uuid = util.get(response, "tasks/0/unique_id")
        response = self.task.delete_task(uuid)

        self.assertTrue(self.verify_structure(response))
        is_deleted = util.get(response, "tasks/0/deleted")
        self.assertTrue(is_deleted)


