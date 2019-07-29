import unittest

from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.file_exporter import FileExporter
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import Tasks


class TestFileExporter(unittest.TestCase):

    def setUp(self) -> None:
        self.db = JsonFileDatabase(db_name="test_file_exporter_db")
        self.tasks = Tasks(self.db)
        self.task1 = Task("Task1")
        self.task1.label = "waiting"
        self.task1.date_expression = "today"
        self.tasks.add(self.task1)
        self.task1.complete()

        self.task2 = Task("Task2")
        self.task2.label = "computer"
        self.task2.date_expression = "today"
        self.tasks.add(self.task2)

        self.task3 = Task("Task3")
        self.task3.label = "office"
        self.task3.date_expression = "today"
        self.tasks.add(self.task3)
        self.task3.complete()

        self.task4 = Task("Task4")
        self.task4.label = "waiting"
        self.task4.date_expression = "today"
        self.tasks.add(self.task4)

        self.task5 = Task("Task5")
        self.task5.label = "office"
        self.task5.date_expression = "today"
        self.tasks.add(self.task5)
        self.task5.complete()

        self.task6 = Task("Task6")
        self.task6.label = "call"
        self.task6.date_expression = "today"
        self.tasks.add(self.task6)
        self.task6.complete()

        self.task7 = Task("Task7")
        self.task7.label = "computer"
        self.task7.date_expression = "today"
        self.tasks.add(self.task7)
        self.task7.complete()

        self.task8 = Task("Task8")
        self.task8.label = "call"
        self.task8.date_expression = "today"
        self.tasks.add(self.task8)

        self.task9 = Task("Task9")
        self.task9.label = "office"
        self.task9.date_expression = "today"
        self.tasks.add(self.task9)
        self.task9.complete()

        self.task10 = Task("Task10")
        self.task10.label = ""
        self.task10.date_expression = "today"
        self.tasks.add(self.task10)

    def tearDown(self):
        self.tasks.clear()
        self.db.remove()

    def test_save(self):
        exporter = FileExporter("/home/cpeterson/tmp")
        exporter.save(self.tasks.get_list())

