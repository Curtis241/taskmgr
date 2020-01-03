import unittest

from taskmgr.lib.model.database import RedisDatabase, DatabaseObject
from taskmgr.lib.model.task import Task


class MissingIterMethod(DatabaseObject):

    def deserialize(self, obj_dict):
        pass

    def __init__(self):
        super().__init__(self.__class__.__name__)


class MissingSubclass:
    pass


class TestRedisDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.redis_db = RedisDatabase("localhost", 6379)
        self.redis_db.clear()

        self.task1 = Task("task1")
        self.task1.index = 1
        self.task2 = Task("task2")
        self.task2.index = 2
        self.task3 = Task("task3")
        self.task3.index = 3
        self.task4 = Task("task4")
        self.task4.index = 4
        self.task5 = Task("task5")
        self.task5.index = 5
        self.task6 = Task("task6")
        self.task6.index = 6
        self.task7 = Task("task7")
        self.task7.index = 7
        self.task8 = Task("task8")
        self.task8.index = 8
        self.task9 = Task("task9")
        self.task9.index = 9
        self.task10 = Task("task10")
        self.task10.index = 10

    def tearDown(self) -> None:
        self.redis_db.clear()

    def test_multiple_insert_using_should_not_create_duplicates(self):
        self.redis_db.set([self.task1, self.task2, self.task3, self.task4, self.task5,
                            self.task6, self.task7, self.task8, self.task9, self.task10])
        self.redis_db.set([self.task1, self.task2, self.task3, self.task4, self.task5,
                            self.task6, self.task7, self.task8, self.task9, self.task10])
        task_list = self.redis_db.to_object_list(self.redis_db.get(), Task())
        self.assertTrue(len(task_list) == 10)

    def test_object_serialization(self):
        self.redis_db.set([self.task1])
        task_list = self.redis_db.to_object_list(self.redis_db.get(), Task())
        self.assertTrue(len(task_list) == 1)

        task = task_list[0]
        self.assertEqual(self.task1.text, task.text)
        self.assertEqual(self.task1.index, task.index)
        self.assertEqual(self.task1.unique_id, task.unique_id)
        self.assertEqual(self.task1.project, task.project)
        self.assertEqual(self.task1.date_expression, task.date_expression)
        self.assertEqual(self.task1.priority, task.priority)
        self.assertEqual(self.task1.label, task.label)

    def test_object_must_be_subclass_of_DatabaseObject(self):
        with self.assertRaises(ValueError):
            self.redis_db.set([MissingSubclass])

    def test_object_must_contain_iter_method(self):
        with self.assertRaises(TypeError):
            self.redis_db.set([MissingIterMethod()])
