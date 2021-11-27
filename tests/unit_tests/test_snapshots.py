import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.snapshot import Snapshot
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

    def test_summarize(self):

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
        snapshot = snapshots.summarize()
        self.assertIsNotNone(snapshot)
        self.assertTrue(snapshot.count == 4)
        self.assertTrue(snapshot.deleted == 1)
        self.assertTrue(snapshot.incomplete == 2)
        self.assertTrue(snapshot.completed == 1)

    def test_get_list(self):
        self.tasks.add("task1", "label1", "project1", "2021-07-14")
        self.tasks.add("task2", "label1", "project1", "2021-09-01")
        self.tasks.add("task3", "label1", "project1", "2021-09-01")
        self.tasks.add("task4", "label1", "project1", "2021-11-01")
        self.tasks.add("task5", "label1", "project1", "empty")
        self.tasks.add("task6", "label1", "project1", "empty")

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_due_date_range("2021-07-13", "2021-11-02")
        snapshot_list = snapshots.get_list()
        self.assertTrue(len(snapshot_list), 3)






