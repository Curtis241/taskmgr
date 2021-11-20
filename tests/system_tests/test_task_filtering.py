import unittest

from dpath import util

from system_tests.common import Common
from system_tests.rest_api import RestApi, Tasks, Task
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.variables import CommonVariables


class TestTaskFiltering(unittest.TestCase):

    def setUp(self) -> None:
        self.api = RestApi()
        self.tasks = Tasks()
        self.task = Task()
        self.vars = CommonVariables()
        self.today = Today()
        self.tasks.remove_all()
        self.util = Common()

    def tearDown(self) -> None: pass

    def test_filter_by_due_date(self):
        self.tasks.add("task1", "project1", "label1", "2019-03-01")
        self.tasks.add("task2", "project1", "label1", "2019-03-01")
        self.tasks.add("task3", "project1", "label1", "2019-03-01")

        self.tasks.reschedule()
        response = self.tasks.filter_by_due_date(self.today.to_date_string())
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 3)

    def test_filter_by_project(self):
        self.tasks.add("task1", "project1", "label1", "today")
        self.tasks.add("task2", "project1", "label1", "today")
        self.tasks.add("task3", "project1", "label1", "today")

        response = self.tasks.filter_by_project("project1")
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 3)

    def test_filter_by_text(self):
        self.tasks.add("my_task", "project1", "label1", "today")

        response = self.tasks.filter_by_text("my_task")
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 1)

    def test_filter_by_label(self):
        self.tasks.add("task1", "project1", "my_label", "today")

        response = self.tasks.filter_by_label("my_label")
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 1)

    def test_filter_by_status(self):
        response = self.tasks.add("task1", "project1", "label1", "today")
        uuid = util.get(response, "tasks/0/unique_id")

        response = self.tasks.filter_by_status("incomplete")
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 1)

        response = self.task.complete_task(uuid)
        self.assertTrue(self.util.verify_structure(response))
        response = self.tasks.filter_by_status("complete")
        self.assertTrue(self.util.count(response) == 1)

        response = self.task.incomplete_task(uuid)
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 1)

    def test_filter_by_due_date_range(self):
        self.tasks.add("task1", "project1", "label1", "2019-03-02")
        self.tasks.add("task2", "project1", "label1", "2019-03-05")
        self.tasks.add("task3", "project1", "label1", "2019-03-08")

        response = self.tasks.filter_by_due_date_range("2019-03-01", "2019-03-05")
        self.assertTrue(self.util.verify_structure(response))
        self.assertTrue(self.util.count(response) == 1)

        response = self.tasks.filter_by_due_date_range("2019-03-01", "2019-03-09")
        self.assertTrue(self.util.count(response) == 3)


