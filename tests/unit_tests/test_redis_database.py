import unittest

from taskmgr.lib.database.manager import DatabaseManager
from taskmgr.lib.model.task import Task


class TestRedisDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.mgr = DatabaseManager()
        self.db = self.mgr.get_tasks_db()
        self.db.clear()
        self.task1 = Task("task1")
        self.task1.index = 1

    def tearDown(self) -> None:
        self.db.clear()

    def test_insert_should_create_object(self):
        self.db.append_object(self.task1)
        self.db.replace_object(self.task1)
        self.assertEqual(len(self.db.get_object_list()), 1)

    def test_object_serialization(self):
        self.db.append_object(self.task1)
        task_list = self.db.get_object_list()
        self.assertTrue(len(task_list) == 1)

        task = task_list[0]
        self.assertEqual(self.task1.name, task.name)
        self.assertEqual(self.task1.label, task.label)
        self.assertEqual(self.task1.index, task.index)
        self.assertEqual(self.task1.unique_id, task.unique_id)
        self.assertEqual(self.task1.project, task.project)
        self.assertEqual(self.task1.time_spent, task.time_spent)
        self.assertEqual(self.task1.due_date, task.due_date)
        self.assertEqual(self.task1.completed, task.completed)
        self.assertEqual(self.task1.deleted, task.deleted)
