# import unittest
#
# from taskmgr.lib.model.task import Task
# from taskmgr.lib.task_metrics import MetricsProcessor
# from taskmgr.lib.presenter.tasks import Tasks
#
#
# class TestTaskMetrics(unittest.TestCase):
#
#     def setUp(self) -> None:
#         self.tasks = Tasks(None)
#
#         self.task1 = Task("Task1")
#         self.task1.deleted = True
#         self.task1.project = "work"
#         self.tasks.add(self.task1)
#
#         self.task2 = Task("Task2")
#         self.task2.complete()
#         self.task2.project = "work"
#         self.tasks.add(self.task2)
#
#         self.task3 = Task("Task3")
#         self.task3.project = "work"
#         self.tasks.add(self.task3)
#
#         self.task4 = Task("Task4")
#         self.task4.deleted = True
#         self.task4.project = "home"
#         self.tasks.add(self.task4)
#
#         self.task5 = Task("Task5")
#         self.task5.complete()
#         self.task5.project = "home"
#         self.tasks.add(self.task5)
#
#         self.task6 = Task("Task6")
#         self.task6.project = "home"
#         self.tasks.add(self.task6)
#
#     def tearDown(self):
#         self.tasks.clear()
#
#     def test_count(self):
#         processor = MetricsProcessor(self.tasks)
#         project_summaries = processor.count_tasks(MetricsProcessor.LOCAL_DB)
#
#         self.assertTrue(len(project_summaries) == 2)
#         summary1 = project_summaries[0]
#         self.assertTrue(summary1.count == 3)
#         self.assertTrue(summary1.deleted == 1)
#         self.assertTrue(summary1.completed == 1)
#         self.assertTrue(summary1.incomplete == 1)
#
#         summary2 = project_summaries[1]
#         self.assertTrue(summary2.count == 3)
#         self.assertTrue(summary2.deleted == 1)
#         self.assertTrue(summary2.completed == 1)
#         self.assertTrue(summary2.incomplete == 1)
# "