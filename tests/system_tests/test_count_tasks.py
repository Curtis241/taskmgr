import unittest
from dpath import util

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

        response = self.tasks.count_all()
        self.assertEqual(util.get(response, "snapshot/summary/count"), 4)
        snapshot_list = util.get(response, "snapshot/list")
        self.assertEqual(len(snapshot_list), 1)

    def test_count_by_due_date(self):
        self.tasks.add("task1", "project1", "label1", "2021-07-11")
        self.tasks.add("task2", "project1", "label1", "2021-07-15")
        self.tasks.add("task3", "project1", "label1", "2021-07-21")
        self.tasks.add("task4", "project1", "label1", "2021-07-13")

        response = self.tasks.count_by_due_date("2021-07-11")
        self.assertEqual(util.get(response, "snapshot/summary/count"), 1)
        snapshot_list = util.get(response, "snapshot/list")
        self.assertEqual(len(snapshot_list), 1)

        response = self.tasks.count_by_due_date_range("2021-07-10", "2021-07-14")
        self.assertEqual(util.get(response, "snapshot/summary/count"), 2)
        snapshot_list = util.get(response, "snapshot/list")
        self.assertEqual(len(snapshot_list), 2)


