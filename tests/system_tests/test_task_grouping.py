import unittest

from dpath import util

from system_tests.common import Common
from system_tests.rest_api import RestApi, Tasks
from taskmgr.lib.model.calendar import Today


class TestTaskGrouping(unittest.TestCase):

    def setUp(self) -> None:
        self.api = RestApi()
        self.tasks = Tasks()
        self.today = Today()
        self.tasks.remove_all()
        self.util = Common()

    def tearDown(self) -> None: pass

    def test_group_by_label(self):
        self.tasks.add("task1", "project1", "label1", "today")
        self.tasks.add("task2", "project1", "label2", "today")
        self.tasks.add("task3", "project1", "label3", "today")
        self.tasks.add("task4", "project1", "label1", "today")
        self.tasks.add("task5", "project1", "label2", "today")
        self.tasks.add("task6", "project1", "label3", "today")

        response = self.tasks.group_by_label()
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count_tasks(response) == 6)

        task1 = self.util.get_by_index(response, 0)
        self.assertTrue(util.get(task1, "label") == "label1")

        task2 = self.util.get_by_index(response, 2)
        self.assertTrue(util.get(task2, "label") == "label2")

        task3 = self.util.get_by_index(response, 4)
        self.assertTrue(util.get(task3, "label") == "label3")