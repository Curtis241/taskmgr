import unittest
from datetime import datetime

from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.presenter.date_generator import DateGenerator, Day, Today
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class TestTasks(unittest.TestCase):

    @staticmethod
    def get_completed_due_dates(due_dates):
        return [due_date for due_date in due_dates if due_date.completed]

    def setUp(self):
        self.db = JsonFileDatabase()
        self.db.initialize(Task())
        self.tasks = Tasks(self.db)
        self.task1 = Task("Task1")
        self.task1.label = "waiting"
        self.task1.date_expression = "may 2"
        self.task1.external_id = 1
        self.tasks.add(self.task1)

        self.task2 = Task("Task2")
        self.task2.label = "computer"
        self.task2.date_expression = "may 3"
        self.tasks.add(self.task2)

        self.task3 = Task("Task3")
        self.task3.label = "office"
        self.task3.date_expression = "may 4"
        self.tasks.add(self.task3)

        self.task4 = Task("Task4")
        self.task4.label = "waiting"
        self.task4.date_expression = "may 5"
        self.tasks.add(self.task4)

        self.task5 = Task("Task5")
        self.task5.label = "office"
        self.task5.date_expression = "may 6"
        self.tasks.add(self.task5)

        self.task6 = Task("Task6")
        self.task6.label = "call"
        self.task6.date_expression = "may 7"
        self.tasks.add(self.task6)

        self.task7 = Task("Task7")
        self.task7.label = "computer"
        self.task7.date_expression = "may 8"
        self.tasks.add(self.task7)

        self.task8 = Task("Task8")
        self.task8.label = "call"
        self.task8.date_expression = "may 9"
        self.tasks.add(self.task8)

        self.task9 = Task("Task9")
        self.task9.label = "office"
        self.task9.date_expression = "may 10"
        self.tasks.add(self.task9)

        self.task10 = Task("Task10")
        self.task10.label = "waiting"
        self.task10.date_expression = "may 11"
        self.tasks.add(self.task10)

    def tearDown(self):
        self.db.clear()

    def test_add_task(self):
        task = Task("Task11")
        self.tasks.add(task)
        task_list = self.tasks.get_object_list()
        self.assertTrue(len(task_list) == 11)

    def test_deleted_task(self):
        self.tasks.delete(self.task1.unique_id)
        task_list = self.tasks.get_object_list()
        self.assertTrue(len(task_list) == 10)
        task = task_list[0]
        self.assertEqual(task.unique_id, self.task1.unique_id)
        self.assertTrue(task.deleted)

    def test_complete_task(self):
        date_generator = DateGenerator()
        current_day = datetime.strptime('2019-05-01', CommonVariables().date_format)
        date_generator.current_day = Day(current_day)
        task = Task("Repetitive task", date_generator)
        task.label = "home"
        task.date_expression = "every sa"
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-05-04', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-05-11', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-05-18', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-05-25', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-06-01', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-06-08', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-06-15', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-06-22', '2019-06-29'])

        task.complete()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_date_string_list(), ['2019-06-29', '2019-06-29'])

        task.complete()
        self.assertTrue(task.is_completed())
        date_string = task.get_date_string_list()
        self.assertListEqual(date_string, ['',''])

    def test_task_is_complete(self):
        task = Task("Simple task")
        task.label = "home"
        task.date_expression = "may 1"
        self.assertTrue(len(self.get_completed_due_dates(task.due_dates)) == 0)
        task.complete()
        self.assertTrue(task.is_completed())

    def test_sorting_by_label(self):
        task_list = self.tasks.get_tasks_by_label("call")
        self.assertTrue(type(task_list), list)
        self.assertTrue(len(task_list) == 2)
        first_task = task_list[0]
        self.assertTrue(first_task.label == "call")

    def test_get_unique_labels(self):
        unique_label_set = self.tasks.get_label_set()
        self.assertSetEqual(unique_label_set, {'office', 'waiting', 'call', 'computer'})

    def test_get_list_by_type(self):
        returned_result = self.tasks.get_list_by_type("label", "call", self.tasks.get_object_list())
        self.assertTrue(len(returned_result) == 2)

    def test_replace(self):
        task = self.tasks.get_task_by_name("Task1")
        task.deleted = True

        existing_task = self.tasks.replace(self.task1, task)
        self.assertTrue(existing_task.deleted)
        self.assertEqual(task.text, "Task1")

    def test_reset(self):
        initial_task = self.tasks.get_task_by_name("Task10")
        self.tasks.reset(initial_task.unique_id)
        self.assertEqual(initial_task.due_dates[0].date_string, "2020-05-11")

        modified_task = self.tasks.get_task_by_name("Task10")
        self.assertTrue(len(modified_task.due_dates) == 1)
        current_date_string = Today().to_date_string()
        self.assertTrue(modified_task.due_dates[0].date_string == current_date_string)


if __name__ == "__main__":
    unittest.main()
