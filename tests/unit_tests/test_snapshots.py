import unittest

from taskmgr.lib.database.manager import DatabaseManager
from taskmgr.lib.presenter.snapshots import Snapshots


class TestSnapshots(unittest.TestCase):

    def setUp(self) -> None:
        self.tasks = DatabaseManager().get_tasks_model()

    def tearDown(self) -> None:
        self.tasks.clear()

    def test_count_all(self):
        self.tasks.add("task1", "label1", "project1", "today")
        t1 = self.tasks.get_task_by_name("task1")
        self.tasks.complete(t1)

        self.tasks.add("task2", "label1", "project1", "today")
        t2 = self.tasks.get_task_by_name("task2")
        self.tasks.delete(t2)

        self.tasks.add("task3", "label1", "project1", "today")
        self.tasks.add("task4", "label1", "project1", "today")

        snapshots = Snapshots(self.tasks)
        snapshots.count_all_tasks()
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertIsNotNone(summary)
        self.assertTrue(summary.count == 4)
        self.assertTrue(summary.deleted == 1)
        self.assertTrue(summary.incomplete == 2)
        self.assertTrue(summary.completed == 1)

    def test_count_by_due_date_range(self):
        self.tasks.add("task1", "label1", "project1", "2021-07-14")
        self.tasks.add("task2", "label1", "project1", "2021-09-01")
        self.tasks.add("task3", "label1", "project1", "2021-09-01")
        self.tasks.add("task4", "label1", "project1", "2021-11-01")

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_due_date_range("2021-07-13", "2021-11-02")
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.count, 4)
        self.assertEqual(summary.completed, 0)
        self.assertEqual(summary.incomplete, 4)
        self.assertEqual(summary.deleted, 0)
        self.assertTrue(len(snapshot_list) == 3)

    def test_count_project(self):
        self.tasks.add("task1", "label1", "project1", "today")
        self.tasks.add("task2", "label1", "project2", "today")
        self.tasks.add("task3", "label1", "project2", "today")
        self.tasks.add("task4", "label1", "project2", "today")

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_project("project2")
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.completed, 0)
        self.assertEqual(summary.incomplete, 3)
        self.assertEqual(summary.deleted, 0)
        self.assertTrue(len(snapshot_list) == 1)

    def test_invalid_operation(self):
        snapshots = Snapshots(self.tasks)
        summary, snapshot_list = snapshots.get_snapshot()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.count, 0)
        self.assertEqual(summary.completed, 0)
        self.assertEqual(summary.incomplete, 0)
        self.assertEqual(summary.deleted, 0)
        self.assertTrue(len(snapshot_list) == 0)






