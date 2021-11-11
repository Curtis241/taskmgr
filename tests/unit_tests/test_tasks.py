import unittest
from datetime import datetime, timedelta

from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class TestTasks(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables()
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.tasks = Tasks(self.db)
        self.task1 = Task("Task1")
        self.task1.label = "waiting"
        self.task1.date_expression = "may 2"
        self.task1.external_id = 1
        self.tasks.append(self.task1)

        self.task2 = Task("Task2")
        self.task2.label = "computer"
        self.task2.date_expression = "may 3"
        self.tasks.append(self.task2)

        self.task3 = Task("Task3")
        self.task3.label = "office"
        self.task3.date_expression = "may 4"
        self.tasks.append(self.task3)

        self.task4 = Task("Task4")
        self.task4.label = "waiting"
        self.task4.date_expression = "may 5"
        self.tasks.append(self.task4)

        self.task5 = Task("Task5")
        self.task5.label = "office"
        self.task5.date_expression = "may 6"
        self.tasks.append(self.task5)

        self.task6 = Task("Task6")
        self.task6.label = "call"
        self.task6.date_expression = "may 7"
        self.tasks.append(self.task6)

        self.task7 = Task("Task7")
        self.task7.label = "computer"
        self.task7.date_expression = "may 8"
        self.tasks.append(self.task7)

        self.task8 = Task("Task8")
        self.task8.label = "call"
        self.task8.date_expression = "may 9"
        self.tasks.append(self.task8)

        self.task9 = Task("Task9")
        self.task9.label = "office"
        self.task9.date_expression = "may 10"
        self.tasks.append(self.task9)

        self.task10 = Task("Task10")
        self.task10.label = "waiting"
        self.task10.date_expression = "may 11"
        self.tasks.append(self.task10)

        self.future_task = Task("Future Task")
        future_datetime = datetime.now() + timedelta(days=1)
        date_string = future_datetime.strftime(self.vars.date_format)
        self.future_task.due_date = DueDate(date_string)
        self.tasks.append(self.future_task)

    def tearDown(self):
        self.db.clear()

    def test_get_task(self):
        task = self.tasks.get_task_by_index(1)
        self.assertTrue(task.index == 1)

    def test_add_task(self):
        task = Task("Task11")
        self.tasks.append(task)
        task_list = self.tasks.get_object_list()
        print(f"test_add_task: len {len(task_list)}")
        self.assertTrue(len(task_list) == 12)

    def test_deleted_task(self):
        self.tasks.delete(self.task1.unique_id)
        task_list = self.tasks.get_object_list()
        self.assertTrue(len(task_list) == 11)
        task = task_list[0]
        self.assertEqual(task.unique_id, self.task1.unique_id)
        self.assertTrue(task.deleted)

    def test_complete_task(self):
        due_date_list = DateGenerator().get_due_dates("every sa")

        tasks = Tasks(self.db)
        tasks.clear_objects()
        tasks.add("Repetitive task","current","home", "every sa")
        task_list = tasks.get_object_list()

        self.assertTrue(len(due_date_list) == len(task_list))

        for task in task_list:
            task.complete()

        for task in task_list:
            self.assertTrue(task.is_completed())

    def test_task_is_complete(self):
        tasks = Tasks(self.db)
        tasks.clear_objects()
        tasks.add("Simple Task", "current", "home", "today")
        task_list = tasks.get_object_list()
        self.assertTrue(len(task_list) == 1)
        task1 = task_list[0]

        self.assertTrue(task1.due_date.date_string == Today().to_date_string())
        task1.complete()
        self.assertTrue(task1.is_completed())

    def test_sorting_by_label(self):
        task_list = self.tasks.get_tasks_by_label("call")
        self.assertTrue(type(task_list), list)
        self.assertTrue(len(task_list) == 2)
        first_task = task_list[0]
        self.assertTrue(first_task.label == "call")

    def test_get_unique_labels(self):
        unique_label_set = self.tasks.get_label_set()
        self.assertSetEqual(unique_label_set, {'office', 'waiting', 'call', 'computer', 'current'})

    def test_get_list_by_type(self):
        returned_result = self.tasks.get_list_by_type("label", "call", self.tasks.get_object_list())
        self.assertTrue(len(returned_result) == 2)

    def test_get_list_by_date_expression(self):
        task_list = self.tasks.get_tasks_by_date("tomorrow")
        self.assertTrue(len(task_list) == 1)
        task = task_list[0]
        self.assertTrue(task.text == "Future Task")

    def test_replace(self):
        task = self.tasks.get_task_by_name("Task1")
        task.deleted = True

        existing_task = self.tasks.replace(self.task1, task)
        self.assertTrue(existing_task.deleted)
        self.assertEqual(task.text, "Task1")

    def test_reset(self):
        tasks = Tasks(self.db)
        tasks.clear_objects()
        tasks.add("InitialTask", "current", "home", "2020-05-11")

        initial_task = tasks.get_task_by_name("InitialTask")
        tasks.reset(initial_task.unique_id)
        self.assertEqual(initial_task.due_date.date_string, "2020-05-11")

        modified_task = tasks.get_task_by_name("InitialTask")
        current_date_string = Today().to_date_string()
        self.assertTrue(modified_task.due_date.date_string == current_date_string)


if __name__ == "__main__":
    unittest.main()
