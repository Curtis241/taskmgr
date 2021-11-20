import unittest

from system_tests.common import Common
from system_tests.rest_api import RestApi, Tasks, Task


class TestCountTasks(unittest.TestCase):

    def setUp(self) -> None:
        self.api = RestApi()
        self.tasks = Tasks()
        self.task = Task()
        self.util = Common()
        self.tasks.remove_all()

    def tearDown(self) -> None: pass

    def test_count_all(self):
        self.tasks.add("task1", "project1", "label1", "today")
        self.tasks.add("task2", "project1", "label1", "today")
        self.tasks.add("task3", "project1", "label1", "today")
        self.tasks.add("task4", "project1", "label1", "today")

        #response = self.tasks.count_all()
        #print(response)
