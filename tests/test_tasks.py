import unittest
from datetime import datetime

from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.date_generator import DateGenerator, Day
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import Tasks, SortType
from taskmgr.lib.variables import CommonVariables


class TestTasks(unittest.TestCase):

    @staticmethod
    def get_completed_due_dates(due_dates):
        return [due_date for due_date in due_dates if due_date.completed]

    def setUp(self):
        self.db = JsonFileDatabase(db_name="test_tasks_file_db")
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
        self.tasks.clear()
        self.db.remove()

    def test_to_dict(self):
        returned_result = self.tasks.to_dict()
        self.assertTrue(type(returned_result) == list)
        self.assertTrue(type(returned_result[0]) == dict)
        self.assertTrue(type(returned_result[1]) == dict)
        self.assertTrue(type(returned_result[2]) == dict)
        self.assertTrue(type(returned_result[3]) == dict)
        self.assertTrue(type(returned_result[4]) == dict)
        self.assertTrue(type(returned_result[5]) == dict)
        self.assertTrue(type(returned_result[6]) == dict)
        self.assertTrue(type(returned_result[7]) == dict)
        self.assertTrue(type(returned_result[8]) == dict)
        self.assertTrue(type(returned_result[9]) == dict)

    def test_from_dict(self):
        tasks_dict_list = [
            {'index': 1, 'text': 'Task1', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'date_expression': 'mar 9',
             'due_dates': [{"date_string": '2019-03-09', "completed": False}]},
            {'index': 2, 'text': 'Task2', 'label': '@computer', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'date_expression': 'mar 9',
             'due_dates': [{"date_string": "2019-03-09", "completed": False}]}]

        self.tasks.from_dict(tasks_dict_list)
        tasks_list = self.tasks.get_list()
        self.assertTrue(len(tasks_list) == 12)

        task1 = tasks_list[10]
        self.assertTrue(len(task1.due_dates) == 1)
        self.assertTrue(task1.due_dates[0].date_string, '2019-03-09')
        self.assertTrue(task1.text == "Task1")

        task2 = tasks_list[11]
        self.assertTrue(len(task2.due_dates) == 1)
        self.assertTrue(task2.due_dates[0].date_string, '2019-03-09')
        self.assertTrue(task2.text == "Task2")

    def test_add_task(self):
        task = Task("Task11")
        self.tasks.add(task)
        task_list = self.tasks.get_list()
        self.assertTrue(len(task_list) == 11)

        self.assertTrue(task.date_expression == "empty")
        self.assertFalse(task.is_completed())

    def test_deleted_task(self):
        self.tasks.delete(self.task1.id)
        task_list = self.tasks.get_list()
        self.assertTrue(len(task_list) == 10)
        task = task_list[0]
        self.assertEqual(task.id, self.task1.id)
        self.assertTrue(task.deleted)

    def test_complete_task(self):
        date_generator = DateGenerator()
        current_day = datetime.strptime('2019-05-01', CommonVariables.date_format)
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
        self.assertIsNone(task.get_date_string_list())

    def test_task_is_complete(self):
        task = Task("Simple task")
        task.label = "home"
        task.date_expression = "may 1"
        self.assertTrue(len(self.get_completed_due_dates(task.due_dates)) == 0)
        task.complete()
        self.assertTrue(task.is_completed())

    def test_sorting_by_label(self):
        task_list = self.tasks.sort(SortType.Label)
        self.assertTrue(type(task_list), list)
        self.assertTrue(len(task_list) == 10)
        first_task = task_list[0]
        self.assertTrue(first_task.label == "call")

    def test_get_unique_labels(self):
        unique_label_set = self.tasks.unique(SortType.Label)
        self.assertSetEqual(unique_label_set, {'office', 'waiting', 'call', 'computer'})

    def test_contains_sort_type(self):
        self.assertTrue(SortType().contains("project"))
        self.assertTrue(SortType().contains("label"))

    def test_get_list_by_type(self):
        returned_result = self.tasks.get_list_by_type(SortType.Label, "call")
        self.assertTrue(len(returned_result) == 2)

    def test_replace(self):
        task = self.tasks.get_task_by_name("Task1")
        task.deleted = True

        existing_task = self.tasks.replace(self.task1, task)
        self.assertTrue(existing_task.deleted)
        self.assertEqual(task.text, "Task1")


if __name__ == "__main__":
    unittest.main()
