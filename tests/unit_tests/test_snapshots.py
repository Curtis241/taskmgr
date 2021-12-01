import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks


class TestSnapshots(unittest.TestCase):

    def setUp(self) -> None:
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.db.clear()
        self.tasks = Tasks(self.db)

    def tearDown(self) -> None:
        self.db.clear()

    def test_count_all(self):

        self.tasks.add("task1", "label1", "project1", "today")
        t1 = self.tasks.get_task_by_name("task1")
        self.tasks.complete(t1.unique_id)

        self.tasks.add("task2", "label1", "project1", "today")
        t2 = self.tasks.get_task_by_name("task2")
        self.tasks.delete(t2.unique_id)

        self.tasks.add("task3", "label1", "project1", "today")
        self.tasks.add("task4", "label1", "project1", "today")

        snapshots = Snapshots(self.tasks)
        snapshots.count_all_tasks()
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertIsNotNone(summary)
        self.assertTrue(summary["count"] == 4)
        self.assertTrue(summary["deleted"] == 1)
        self.assertTrue(summary["incomplete"] == 2)
        self.assertTrue(summary["completed"] == 1)

    def test_count_by_due_date_range(self):
        self.tasks.add("task1", "label1", "project1", "2021-07-14")
        self.tasks.add("task2", "label1", "project1", "2021-09-01")
        self.tasks.add("task3", "label1", "project1", "2021-09-01")
        self.tasks.add("task4", "label1", "project1", "2021-11-01")

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_due_date_range("2021-07-13", "2021-11-02")
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertDictEqual(summary, {'count': 4, 'completed': 0, 'incomplete': 4, 'deleted': 0})
        self.assertTrue(len(snapshot_list) == 3)

    def test_count_project(self):
        self.tasks.add("task1", "label1", "project1", "today")
        self.tasks.add("task2", "label1", "project2", "today")
        self.tasks.add("task3", "label1", "project2", "today")
        self.tasks.add("task4", "label1", "project2", "today")

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_project("project2")
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertDictEqual(summary, {'count': 3, 'completed': 0, 'incomplete': 3, 'deleted': 0})
        self.assertTrue(len(snapshot_list) == 1)

    def test_invalid_operation(self):
        snapshots = Snapshots(self.tasks)
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertDictEqual(summary, {'count': 0, 'completed': 0, 'incomplete': 0, 'deleted': 0})
        self.assertTrue(len(snapshot_list) == 0)






