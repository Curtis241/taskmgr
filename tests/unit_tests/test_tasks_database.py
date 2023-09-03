import unittest

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.task import Task
from taskmgr.lib.variables import CommonVariables


class TestTasksDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.vars = CommonVariables('test_variables.ini')
        self.mgr = DatabaseManager(self.vars)
        self.db = self.mgr.get_tasks_db()
        self.db.clear()

        self.t1 = Task("t1")
        self.t1.project = "p1"
        self.t1.status = "s1"
        self.t1.label = "l1"
        self.t1.index = 1
        self.t1.unique_id = self.db.get_unique_id()

        self.t2 = Task("t2")
        self.t2.project = "p2"
        self.t2.status = "s2"
        self.t2.label = "l2"
        self.t2.index = 2
        self.t2.unique_id = self.db.get_unique_id()

        self.t3 = Task("t3")
        self.t3.project = "p3"
        self.t3.status = "s3"
        self.t3.label = "l3"
        self.t3.index = 3
        self.t3.unique_id = self.db.get_unique_id()

    def tearDown(self) -> None:
        self.db.clear()

    def test_insert_should_create_object(self):
        self.db.append_object(self.t1)
        self.db.replace_object(self.t1)
        result = self.db.get_all()
        self.assertEqual(result.item_count, 1)

    def test_get_task(self):
        self.db.append_object(self.t1)
        task = self.db.get_object("name", "t1")
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "t1")

    def test_get_tasks_containing_name(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("name", "t1")
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "t1")

    def test_get_tasks_by_index(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("index", 2)
        self.assertEqual(task.name, "t2")

    def test_get_tasks_by_id(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("unique_id", self.t1.unique_id)
        self.assertEqual(task.unique_id, self.t1.unique_id)

    def test_get_tasks_by_status(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("completed", self.t2.completed)
        self.assertEqual(task.completed, self.t2.completed)

    def test_get_tasks_by_project(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("project", self.t1.project)
        self.assertEqual(task.project, self.t1.project)

    def test_get_tasks_by_label(self):
        self.db.append_objects([self.t1, self.t2, self.t3])
        task = self.db.get_object("label", self.t1.label)
        self.assertEqual(task.label, self.t1.label)

    def test_aggregate_label(self):
        self.t1.label = "my_label"
        self.t2.label = "my_label"
        self.t3.label = "my_label"
        self.db.append_objects([self.t1, self.t2, self.t3])
        label_list = self.db.unique("label")
        self.assertListEqual(label_list, ["my_label"])

    def test_aggregate_project(self):
        self.t1.project = "my_project"
        self.t2.project = "my_project"
        self.t3.project = "my_project"
        
        self.db.append_objects([self.t1, self.t2, self.t3])
        project_list = self.db.unique("project")
        self.assertListEqual(project_list, ["my_project"])

    def test_aggregate_due_date(self):
        self.t1.due_date = "2019-07-01"
        self.t2.due_date = "2019-07-01"
        self.t3.due_date = "2019-07-01"

        self.db.append_objects([self.t1, self.t2, self.t3])
        due_date_list = self.db.unique("due_date")
        self.assertListEqual(due_date_list, ["2019-07-01"])

    def test_object_serialization(self):
        self.db.append_object(self.t1)
        result = self.db.get_all()
        self.assertTrue(result.item_count == 1)

        task_list = result.to_list()
        task = task_list[0]
        self.assertEqual(self.t1.name, task.name)
        self.assertEqual(self.t1.label, task.label)
        self.assertEqual(self.t1.index, task.index)
        self.assertEqual(self.t1.unique_id, task.unique_id)
        self.assertEqual(self.t1.project, task.project)
        self.assertEqual(self.t1.time_spent, task.time_spent)
        self.assertEqual(self.t1.due_date, task.due_date)
        self.assertEqual(self.t1.completed, task.completed)
        self.assertEqual(self.t1.deleted, task.deleted)
