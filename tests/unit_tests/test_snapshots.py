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
        self.snapshots.update([t1])

        self.tasks.add("task2", "label1", "project1", "today")
        t2 = self.tasks.get_task_by_name("task2")
        self.tasks.delete(t2)
        self.snapshots.update([t2])

        t3_list = self.tasks.add("task3", "label1", "project1", "today")
        self.snapshots.update(t3_list)
        t4_list = self.tasks.add("task4", "label1", "project1", "today")
        self.snapshots.update(t4_list)

        result = self.snapshots.get_all()
        self.assertEqual(result.item_count, 1)
        summary_list = result.to_list()
        summary = summary_list[0]

        self.assertIsNotNone(summary)
        self.assertTrue(summary.task_count == 4)
        self.assertTrue(summary.delete_count == 1)
        self.assertTrue(summary.incomplete_count == 3)
        self.assertTrue(summary.complete_count == 1)

    def test_count_by_due_date_range(self):
        t1_list = self.tasks.add("task1", "label1", "project1", "2021-07-14")
        self.snapshots.update(t1_list)
        t2_list = self.tasks.add("task2", "label1", "project1", "2021-09-01")
        self.snapshots.update(t2_list)
        t3_list = self.tasks.add("task3", "label1", "project1", "2021-09-01")
        self.snapshots.update(t3_list)
        t4_list = self.tasks.add("task4", "label1", "project1", "2021-11-01")
        self.snapshots.update(t4_list)

        result = self.snapshots.get_by_due_date_range("2021-07-13", "2021-11-02")
        self.assertEqual(result.item_count, 3)

    def test_summarize(self):
        self.tasks.add("task1", "label1", "project1", "2021-07-12")
        self.tasks.add("task2", "label1", "project1", "2021-07-13")
        self.tasks.add("task3", "label1", "project1", "2021-07-14")
        self.tasks.add("task4", "label1", "project1", "2021-07-15")
        result = self.tasks.get_all()
        snapshot_list = self.snapshots.summarize(result.to_list())

        self.assertEqual(len(snapshot_list), 4)
        self.assertEqual(snapshot_list[0].task_count, 1)
        self.assertEqual(snapshot_list[0].due_date, "2021-07-12")
        self.assertEqual(snapshot_list[1].task_count, 1)
        self.assertEqual(snapshot_list[1].due_date, "2021-07-13")
        self.assertEqual(snapshot_list[2].task_count, 1)
        self.assertEqual(snapshot_list[2].due_date, "2021-07-14")
        self.assertEqual(snapshot_list[3].task_count, 1)
        self.assertEqual(snapshot_list[3].due_date, "2021-07-15")

    def test_summarize_and_fill(self):
        t1_list = self.tasks.add("task1", "label1", "project1", "2021-07-12")
        self.tasks.add("task2", "label1", "project1", "2021-07-12")
        self.tasks.add("task3", "label1", "project1", "2021-07-12")
        self.tasks.add("task4", "label1", "project1", "2021-07-12")

        snapshot_list = self.snapshots.summarize_and_fill(t1_list)
        self.assertEqual(len(snapshot_list), 1)
        self.assertEqual(snapshot_list[0].task_count, 4)
        self.assertEqual(snapshot_list[0].due_date, "2021-07-12")








