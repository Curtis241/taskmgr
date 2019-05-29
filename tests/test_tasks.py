from datetime import datetime
import unittest

from taskmgr.lib.date_generator import DateGenerator, Day
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import Tasks, SortType
from taskmgr.lib.variables import CommonVariables


class TestTasks(unittest.TestCase):

    @staticmethod
    def get_completed_due_dates(due_dates):
        return [due_date for due_date in due_dates if due_date.completed]

    def setUp(self):
        self.tasks = Tasks()
        task1 = Task("Task1")
        task1.label = "waiting"
        task1.date_expression = "may 2"
        self.tasks.add(task1)

        task2 = Task("Task2")
        task2.label = "computer"
        task2.date_expression = "may 3"
        self.tasks.add(task2)

        task3 = Task("Task3")
        task3.label = "office"
        task3.date_expression = "may 4"
        self.tasks.add(task3)

        task4 = Task("Task4")
        task4.label = "waiting"
        task4.date_expression = "may 5"
        self.tasks.add(task4)

        task5 = Task("Task5")
        task5.label = "office"
        task5.date_expression = "may 6"
        self.tasks.add(task5)

        task6 = Task("Task6")
        task6.label = "call"
        task6.date_expression = "may 7"
        self.tasks.add(task6)

        task7 = Task("Task7")
        task7.label = "computer"
        task7.date_expression = "may 8"
        self.tasks.add(task7)

        task8 = Task("Task8")
        task8.label = "call"
        task8.date_expression = "may 9"
        self.tasks.add(task8)

        task9 = Task("Task9")
        task9.label = "office"
        task9.date_expression = "may 10"
        self.tasks.add(task9)

        task10 = Task("Task10")
        task10.label = "waiting"
        task10.date_expression = "may 11"
        self.tasks.add(task10)

    def tearDown(self):
        self.tasks.clear()

    def test_to_dict(self):
        returned_result = self.tasks.to_dict()
        expected_result = [
            {'index': 1, 'text': 'Task1', 'label': '@waiting', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 2', 'due_dates': [{'date_string': '2019-05-02', 'completed': False}]},
            {'index': 2, 'text': 'Task2', 'label': '@computer', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 3', 'due_dates': [{'date_string': '2019-05-03', 'completed': False}]},
            {'index': 3, 'text': 'Task3', 'label': '@office', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 4', 'due_dates': [{'date_string': '2019-05-04', 'completed': False}]},
            {'index': 4, 'text': 'Task4', 'label': '@waiting', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 5', 'due_dates': [{'date_string': '2019-05-05', 'completed': False}]},
            {'index': 5, 'text': 'Task5', 'label': '@office', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 6', 'due_dates': [{'date_string': '2019-05-06', 'completed': False}]},
            {'index': 6, 'text': 'Task6', 'label': '@call', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 7', 'due_dates': [{'date_string': '2019-05-07', 'completed': False}]},
            {'index': 7, 'text': 'Task7', 'label': '@computer', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 8', 'due_dates': [{'date_string': '2019-05-08', 'completed': False}]},
            {'index': 8, 'text': 'Task8', 'label': '@call', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 9', 'due_dates': [{'date_string': '2019-05-09', 'completed': False}]},
            {'index': 9, 'text': 'Task9', 'label': '@office', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 10', 'due_dates': [{'date_string': '2019-05-10', 'completed': False}]},
            {'index': 10, 'text': 'Task10', 'label': '@waiting', 'deleted': False, 'priority': 1, 'project': 'inbox',
             'date_expression': 'may 11', 'due_dates': [{'date_string': '2019-05-11', 'completed': False}]}]

        print("returned_result: {}".format(returned_result))
        print("expected_result: {}".format(expected_result))
        self.assertCountEqual(returned_result, expected_result)

    def test_from_dict(self):
        tasks_dict_list = [
            {'index': 1, 'text': 'Task1', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'date_expression': 'mar 9',
             'due_dates': [{"date_string": '2019-03-09', "completed": False}]},
            {'index': 2, 'text': 'Task2', 'label': '@computer', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'date_expression': 'mar 9',
             'due_dates': [{"date_string": "2019-03-09", "completed": False}]}]

        tasks = Tasks()
        tasks.from_dict(tasks_dict_list)
        tasks_list = tasks.get_list()
        self.assertTrue(len(tasks_list) == 2)

        task1 = tasks_list[0]
        self.assertTrue(len(task1.due_dates) == 1)
        self.assertTrue(task1.due_dates[0].date_string, '2019-03-09')
        self.assertTrue(task1.text == "Task1")

        task2 = tasks_list[1]
        self.assertTrue(len(task2.due_dates) == 1)
        self.assertTrue(task2.due_dates[0].date_string, '2019-03-09')
        self.assertTrue(task2.text == "Task2")

    def test_add_task(self):
        self.tasks.add(Task("Task11"))
        task_list = self.tasks.get_list()
        self.assertTrue(len(task_list) == 11)

    def test_delete_task(self):
        self.tasks.delete(2)
        task_list = self.tasks.get_list()
        self.assertTrue(len(task_list) == 9)

    def test_complete_task(self):
        date_generator = DateGenerator()
        current_day = datetime.strptime('2019-05-01', CommonVariables.date_format)
        date_generator.current_day = Day(current_day)
        task = Task("Repetitive task", date_generator)
        task.label = "home"
        task.date_expression = "every sa"
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-05-04', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-05-11', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-05-18', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-05-25', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-06-01', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-06-08', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-06-15', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-06-22', '2019-06-29'])

        task.complete_due_date()
        self.assertFalse(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, False, 'Repetitive task', 'inbox', '@home', '2019-06-29', '2019-06-29'])

        task.complete_due_date()
        self.assertTrue(task.is_completed())
        self.assertListEqual(task.get_task_status(),
                             [0, True, 'Repetitive task', 'inbox', '@home', '', ''])

    def test_task_is_complete(self):
        task = Task("Simple task")
        task.label = "home"
        task.date_expression = "may 1"
        self.assertTrue(len(self.get_completed_due_dates(task.due_dates)) == 0)
        task.complete_due_date()
        self.assertTrue(task.is_completed())

    def test_sorting_by_label(self):
        task_list = self.tasks.sort(SortType.Label)
        self.assertTrue(type(task_list), list)
        self.assertTrue(len(task_list) == 10)
        first_task = task_list[0]
        self.assertTrue(first_task.label == "@call")

    def test_get_unique_labels(self):
        unique_label_set = self.tasks.unique(SortType.Label)
        self.assertSetEqual(unique_label_set, {'@office', '@waiting', '@call', '@computer'})

    def test_contains_sort_type(self):
        self.assertTrue(SortType().contains("project"))
        self.assertTrue(SortType().contains("label"))

    def test_get_list_by_type(self):
        returned_result = self.tasks.get_list_by_type(SortType.Label, "@call")
        self.assertTrue(len(returned_result) == 2)


if __name__ == "__main__":
    unittest.main()
