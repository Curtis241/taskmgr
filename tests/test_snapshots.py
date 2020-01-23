import unittest

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks


class TestSnapshots(unittest.TestCase):

    def setUp(self) -> None:
        self.db = JsonFileDatabase()
        self.db.initialize(Snapshot())
        self.snapshots = Snapshots(self.db)

        self.snapshot1 = Snapshot()
        self.snapshot1.project = "work"
        self.snapshot1.count = 100
        self.snapshot1.deleted = 55
        self.snapshot1.incomplete = 22
        self.snapshot1.completed = 33

    def tearDown(self) -> None:
        self.db.clear()

    def test_add_snapshot(self):
        self.snapshots.add(self.snapshot1)
        snapshot_list = self.snapshots.get_object_list()
        self.assertIsNotNone(snapshot_list)
        self.assertTrue(len(snapshot_list) == 1)

    def test_count_tasks(self):
        json_db = JsonFileDatabase()
        json_db.initialize(Task())
        json_db.clear()
        tasks = Tasks(json_db)

        task1 = Task()
        task1.project = "work"
        task1.label = "current"
        task1.text = "task1"
        task1.complete()
        task1.priority = 1

        task2 = Task()
        task2.project = "work"
        task2.label = "current"
        task2.text = "task2"
        task2.priority = 1

        task3 = Task()
        task3.project = "work"
        task3.label = "current"
        task3.text = "task1"
        task3.deleted = True
        task3.priority = 1

        tasks.add(task1)
        tasks.add(task2)
        tasks.add(task3)

        snapshot_list = self.snapshots.count_tasks(tasks)
        self.assertIsNotNone(snapshot_list)
        self.assertTrue(len(snapshot_list) == 1)
        snapshot = snapshot_list[0]

        self.assertTrue(snapshot.count == 3)
        self.assertTrue(snapshot.deleted == 1)
        self.assertTrue(snapshot.incomplete == 1)
        self.assertTrue(snapshot.completed == 1)






