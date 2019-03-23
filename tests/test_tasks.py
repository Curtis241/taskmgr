import unittest

from taskmgr.lib.task import Task
from taskmgr.lib.tasks import Tasks, SortType


class TestTasks(unittest.TestCase):

    def setUp(self):
        self.tasks = Tasks()
        task1 = Task("Task1")
        task1.label = "waiting"
        self.tasks.add(task1)

        task2 = Task("Task2")
        task2.label = "computer"
        self.tasks.add(task2)

        task3 = Task("Task3")
        task3.label = "office"
        self.tasks.add(task3)

        task4 = Task("Task4")
        task4.label = "waiting"
        self.tasks.add(task4)

        task5 = Task("Task5")
        task5.label = "office"
        self.tasks.add(task5)

        task6 = Task("Task6")
        task6.label = "call"
        self.tasks.add(task6)

        task7 = Task("Task7")
        task7.label = "computer"
        self.tasks.add(task7)

        task8 = Task("Task8")
        task8.label = "call"
        self.tasks.add(task8)

        task9 = Task("Task9")
        task9.label = "office"
        self.tasks.add(task9)

        task10 = Task("Task10")
        task10.label = "waiting"
        self.tasks.add(task10)

    def tearDown(self): pass

    def test_to_dict(self):
        returned_result = self.tasks.to_dict()
        expected_result = [
            {'index': 1, 'text': 'Task1', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 2, 'text': 'Task2', 'label': '@computer', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 3, 'text': 'Task3', 'label': '@office', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 4, 'text': 'Task4', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 5, 'text': 'Task5', 'label': '@office', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 6, 'text': 'Task6', 'label': '@call', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 7, 'text': 'Task7', 'label': '@computer', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 8, 'text': 'Task8', 'label': '@call', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 9, 'text': 'Task9', 'label': '@office', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []},
            {'index': 10, 'text': 'Task10', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': []}]

        print("returned_result: {}".format(returned_result))
        print("expected_result: {}".format(expected_result))
        self.assertCountEqual(returned_result, expected_result)

    def test_from_dict(self):
        tasks_dict_list = [
            {'index': 1, 'text': 'Task1', 'label': '@waiting', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': ['2019-03-09']},
            {'index': 2, 'text': 'Task2', 'label': '@computer', 'completed': False, 'deleted': False, 'priority': 1,
             'project': 'inbox', 'due_date': ['2019-03-09']}]

        tasks = Tasks()
        tasks.from_dict(tasks_dict_list)
        tasks_list = tasks.get_list()
        self.assertTrue(len(tasks_list) == 2)

        task1 = tasks_list[0]
        self.assertListEqual(task1.due_date, ['2019-03-09'])
        self.assertTrue(task1.text == "Task1")

        task2 = tasks_list[1]
        self.assertListEqual(task2.due_date, ["2019-03-09"])
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
        self.tasks.complete(2)
        task_list = self.tasks.get_list()
        self.assertTrue(len(task_list) == 10)
        task = task_list[1]
        self.assertTrue(task.is_complete)

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
