import unittest

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.variables import CommonVariables


class TestTasks(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables()
        self.tasks = DatabaseManager().get_tasks_model()

    def tearDown(self):
        self.tasks.clear()

    def test_get_task(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        task = self.tasks.get_task_by_index(1)
        self.assertTrue(task.index == 1)

    def test_add_task(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        self.tasks.add("Task2", "computer", "work", "may 3")
        self.tasks.add("Task3", "office", "work", "may 4")
        self.tasks.add("Task4", "waiting", "work", "may 5")
        self.tasks.add("Task5", "office", "work", "may 6")
        self.tasks.add("Task6", "call", "work", "may 7")
        self.tasks.add("Task7", "computer", "work", "may 8")
        self.tasks.add("Task8", "call", "work", "may 9")
        self.tasks.add("Task9", "office", "work", "may 10")
        self.tasks.add("Task10", "default", "default", "may 12")
        result = self.tasks.get_all()
        task_list = result.to_list()
        self.assertTrue(len(task_list) == 10)

    def test_edit_label_task(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        original_task = self.tasks.get_task_by_name("Task1")
        original_task, modified_task = self.tasks.edit(original_task.index, label="waiting2")
        self.assertEqual(modified_task.label, "waiting2")

    def test_edit_project_task(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        original_task = self.tasks.get_task_by_name("Task1")
        original_task, modified_task = self.tasks.edit(original_task.index, project="work2")
        self.assertEqual(modified_task.project, "work2")

    def test_deleted_task(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        existing_task = self.tasks.get_task_by_name("Task1")
        deleted_task = self.tasks.delete(existing_task)

        self.assertEqual(existing_task, deleted_task)
        self.assertTrue(deleted_task.deleted)

    def test_complete_task(self):
        due_date_list = DateGenerator().get_due_dates("every sa")
        self.tasks.add("RepetitiveTask", "current", "home", "every sa")
        result = self.tasks.get_tasks_containing_name("RepetitiveTask")
        task_list = result.to_list()

        self.assertTrue(len(due_date_list) == len(task_list))

        for task in task_list:
            task.completed = True

        for task in task_list:
            self.assertTrue(task.completed)

    def test_task_is_complete(self):
        self.tasks.add("Simple Task", "current", "home", "today")
        task = self.tasks.get_task_by_name("Simple Task")
        self.assertIsNotNone(task)
        self.assertTrue(task.due_date == Today().to_date_string())
        completed_task = self.tasks.complete(task)
        self.assertTrue(completed_task.completed)

    def test_sorting_by_label(self):
        self.tasks.add("Task1", "call", "work", "may 7")
        self.tasks.add("Task2", "call", "work", "may 9")

        result = self.tasks.get_tasks_by_label("call")
        task_list = result.to_list()
        self.assertTrue(type(task_list), list)
        self.assertTrue(len(task_list) == 2)
        first_task = task_list[0]
        self.assertTrue(first_task.label == "call")

    def test_get_unique_labels(self):
        self.tasks.add("Task1", "call", "work", "may 7")
        self.tasks.add("Task2", "waiting", "work", "may 2")
        self.tasks.add("Task3", "computer", "work", "may 3")
        self.tasks.add("Task4", "office", "work", "may 4")
        unique_label_list = self.tasks.get_label_list()
        self.assertListEqual(unique_label_list, ['call', 'computer', 'office', 'waiting'])

    def test_get_list_by_date_expression(self):
        self.tasks.add("FutureTask", "waiting", "work", "tomorrow")
        result = self.tasks.get_tasks_by_date("tomorrow")
        task_list = result.to_list()
        self.assertTrue(len(task_list) == 1)
        task = task_list[0]
        self.assertTrue(task.name == "FutureTask")

    def test_replace(self):
        self.tasks.add("Task1", "waiting", "work", "may 2")
        local_task = self.tasks.get_task_by_name("Task1")

        remote_task = Task("Task1")
        remote_task.index = 1
        remote_task.project = "work"
        remote_task.label = "office"
        remote_task.deleted = True

        replaced_task = self.tasks.replace(local_task, remote_task)
        self.assertTrue(replaced_task.deleted)
        self.assertEqual(replaced_task.name, "Task1")

    def test_reset(self):
        self.tasks.add("InitialTask", "current", "home", "2020-05-11")

        initial_task = self.tasks.get_task_by_name("InitialTask")
        self.assertEqual(initial_task.due_date, "2020-05-11")
        modified_task = self.tasks.reset(initial_task)

        current_date_string = Today().to_date_string()
        self.assertTrue(modified_task.due_date == current_date_string)

    def test_reschedule_tasks(self):
        self.tasks.add("CurrentTask", "waiting", "work", "today")
        task1 = self.tasks.get_task_by_name("CurrentTask")
        self.assertIsNotNone(task1)

        # Deleted tasks should not be rescheduled
        self.tasks.add("task2", "label2", "project2", "2021-10-22")
        task2 = self.tasks.get_task_by_name("task2")
        self.assertIsNotNone(task2)
        self.tasks.delete(task2)

        # Completed tasks should not be rescheduled
        self.tasks.add("task3", "label3", "project3", "2021-10-22")
        task3 = self.tasks.get_task_by_name("task3")
        self.assertIsNotNone(task3)
        self.tasks.complete(task3)

        self.tasks.reschedule()

        result = self.tasks.get_tasks_by_date(Today().to_date_string())
        task_list = result.to_list()
        self.assertTrue(len(task_list) == 1)
        rescheduled_task = task_list[0]
        self.assertEqual(rescheduled_task.name, "CurrentTask")

    def test_get_task_containing_name(self):
        # special characters - : need to be escaped using \.
        # https://redis.io/docs/stack/search/reference/escaping/
        self.tasks.add("ABC\-1343\: Task1", "project", "work", "may 2")
        self.tasks.add("ABC\-1344\: Task2", "project", "work", "may 3")
        self.tasks.add("ABC\-1344\: Task3", "project", "work", "may 4")
        self.tasks.add("ABC\-1422\: Task4", "project", "work", "may 5")
        result = self.tasks.get_tasks_containing_name("ABC\-1344\:")
        task_list = result.to_list()
        self.assertEqual(len(task_list), 2)


if __name__ == "__main__":
    unittest.main()
