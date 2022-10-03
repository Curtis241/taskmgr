import unittest

from taskmgr.lib.database.db_manager import DatabaseManager


class TestSnapshots(unittest.TestCase):

    def setUp(self) -> None:
        self.tasks = DatabaseManager().get_tasks_model()
        self.tasks.clear()

        self.snapshots = DatabaseManager().get_snapshots_model()
        self.snapshots.clear()

    def tearDown(self) -> None:
        self.tasks.clear()
        self.snapshots.clear()

    def test_count_all(self):
        self.tasks.add("task1", "label1", "project1", "today")
        t1 = self.tasks.get_task_by_name("task1")
        self.tasks.complete(t1)

        self.tasks.add("task2", "label1", "project1", "today")
        t2 = self.tasks.get_task_by_name("task2")
        self.tasks.delete(t2)

        self.tasks.add("task3", "label1", "project1", "today")
        self.tasks.add("task4", "label1", "project1", "today")

        snapshot_list = self.snapshots.get_all()
        self.assertEqual(snapshot_list.count(), 1)
        summary = snapshot_list[0]

        self.assertIsNotNone(summary)
        self.assertTrue(summary.task_count == 4)
        self.assertTrue(summary.delete_count == 1)
        self.assertTrue(summary.incomplete_count == 3)
        self.assertTrue(summary.complete_count == 1)

    def test_count_by_due_date_range(self):
        self.tasks.add("task1", "label1", "project1", "2021-07-14")
        self.tasks.add("task2", "label1", "project1", "2021-09-01")
        self.tasks.add("task3", "label1", "project1", "2021-09-01")
        self.tasks.add("task4", "label1", "project1", "2021-11-01")

        snapshot_list = self.snapshots.count_tasks_by_due_date_range("2021-07-13", "2021-11-02")
        self.assertEqual(snapshot_list.count(), 3)

    def test_count_project(self):
        self.tasks.add("task1", "label1", "project1", "today")
        self.tasks.add("task2", "label1", "project2", "today")
        self.tasks.add("task3", "label1", "project2", "today")
        self.tasks.add("task4", "label1", "project2", "today")

        snapshot_list = self.snapshots.count_tasks_by_project("project2")
        self.assertEqual(snapshot_list.count(), 1)







