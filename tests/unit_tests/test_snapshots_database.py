import unittest

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.variables import CommonVariables
from unit_tests.date_parser import DateParser


class TestSnapshotsDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.vars = CommonVariables('test_variables.ini')
        self.mgr = DatabaseManager(self.vars)
        self.db = self.mgr.get_snapshots_db()
        self.db.clear()

        self.s1 = Snapshot()
        self.s1.task_count = 12
        self.s1.incomplete_count = 2
        self.s1.delete_count = 1
        self.s1.complete_count = 9
        self.s1.total_time = 8.0
        self.s1.due_date = "2022-08-21"
        self.s1.due_date_timestamp = DateParser(self.s1.due_date).to_timestamp()
        self.s1.unique_id = self.db.get_unique_id()

        self.s2 = Snapshot()
        self.s2.task_count = 8
        self.s2.incomplete_count = 2
        self.s2.delete_count = 1
        self.s2.complete_count = 5
        self.s2.total_time = 8.0
        self.s2.due_date = "2022-08-22"
        self.s2.due_date_timestamp = DateParser(self.s2.due_date).to_timestamp()
        self.s2.unique_id = self.db.get_unique_id()

        self.s3 = Snapshot()
        self.s3.task_count = 7
        self.s3.incomplete_count = 0
        self.s3.delete_count = 0
        self.s3.complete_count = 7
        self.s3.total_time = 8.0
        self.s3.due_date = "2022-08-23"
        self.s3.due_date_timestamp = DateParser(self.s3.due_date).to_timestamp()
        self.s3.unique_id = self.db.get_unique_id()

    def tearDown(self) -> None:
        self.db.clear()

    def test_insert_should_create_object(self):
        self.db.append_object(self.s1)
        self.db.replace_object(self.s1)
        result = self.db.get_all()
        self.assertEqual(result.item_count, 1)

    def test_get_snapshot(self):
        self.db.append_object(self.s1)
        result = self.db.get_selected("due_date_timestamp",
                                      self.s1.due_date_timestamp,
                                      self.s1.due_date_timestamp)
        self.assertEqual(result.item_count, 1)
        task_list = result.to_list()
        task = task_list[0]
        self.assertEqual(task.due_date, "2022-08-21")

    def test_get_snapshots_by_index(self):
        self.db.append_objects([self.s1, self.s2, self.s3])
        snapshot = self.db.get_object("index", 2)
        self.assertEqual(snapshot.index, 2)

    def test_get_snapshots_by_id(self):
        self.db.append_objects([self.s1, self.s2, self.s3])
        snapshot = self.db.get_object("unique_id", self.s1.unique_id)
        self.assertEqual(snapshot.unique_id, self.s1.unique_id)

    def test_object_serialization(self):
        self.db.append_object(self.s1)
        result = self.db.get_all()
        self.assertEqual(result.item_count, 1)

        snapshot_list = result.to_list()
        snapshot = snapshot_list[0]
        self.assertEqual(self.s1.index, snapshot.index)
        self.assertEqual(self.s1.due_date, snapshot.due_date)
        self.assertEqual(int(self.s1.task_count), int(snapshot.task_count))
        self.assertEqual(int(self.s1.incomplete_count), int(snapshot.incomplete_count))
        self.assertEqual(int(self.s1.complete_count), int(snapshot.complete_count))
        self.assertEqual(int(self.s1.delete_count), int(snapshot.delete_count))
        self.assertEqual(float(self.s1.total_time), float(snapshot.total_time))
