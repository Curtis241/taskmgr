from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import CsvFileImporter
from taskmgr.lib.view.client import Client
from taskmgr.lib.view.snapshot_console_table import SnapshotConsoleTable
from taskmgr.lib.view.task_console_table import TaskConsoleTable
from taskmgr.lib.view.variable_console_table import VariableConsoleTable


class CliClient(Client):
    """
    Provides cli specific features.
    """
    logger = AppLogger("cli_client").get_logger()

    def __init__(self, db_manager, file_manager):
        super().__init__(db_manager)

        assert isinstance(file_manager, FileManager)
        self.__file_manager = file_manager

        self.task_table = TaskConsoleTable()
        self.snapshots_table = SnapshotConsoleTable()
        self.variables_table = VariableConsoleTable()

    def display_tasks(self, task_list):
        return self.__print_tasks_table(task_list)

    def display_snapshots(self, snapshot_list):
        return self.__print_snapshots_table(snapshot_list)

    def list_labels(self):
        """
        Lists all labels contained in the tasks
        :return:
        """
        print("Labels: {}".format(self.get_unique_label_list()))

    def list_projects(self):
        """
        Lists all projects contained in the tasks
        :return:
        """
        print("Projects: {}".format(self.get_unique_project_list()))

    def list_default_variables(self):
        for key, value in self.get_variables_list():
            self.variables_table.add_row([key, value])
        self.variables_table.print()

    def __print_tasks_table(self, task_list):
        self.task_table.clear()
        for task in task_list:
            self.task_table.add_row(task)
        return self.task_table.print()

    def __print_snapshots_table(self, snapshot_list):
        self.snapshots_table.clear()
        for snapshot in snapshot_list:
            self.snapshots_table.add_row(snapshot)
        return self.snapshots_table.print()

    def export_tasks(self, task_list):
        self.__file_manager.save_tasks(task_list)

    def export_snapshots(self, snapshot_list: list):
        self.__file_manager.save_snapshots(snapshot_list)

    def import_tasks(self, csv_file_importer: CsvFileImporter, path: str):
        """
        Imports tasks from the Csv file.
        :param csv_file_importer: CsvFileImporter class
        :param path: path to csv file
        :return: None
        """
        assert isinstance(csv_file_importer, CsvFileImporter)
        assert type(path) is str

        start_datetime = datetime.now()
        self.logger.info(f"Starting import")
        obj_list = self.__file_manager.open_tasks(path)
        self.logger.info(f"Retrieved {len(obj_list)} tasks from file")
        task_list = csv_file_importer.convert(obj_list)
        sync_results = csv_file_importer.import_tasks(task_list)
        self.logger.info(f"Import summary: {sync_results.get_summary()}")

        self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")

    def add_task(self, text: str, label: str, project: str, date_expression: str) -> List[Task]:
        """
        Adds a task
        :param text: text string describing the task
        :param label: label for the task
        :param project: project name for the task
        :param date_expression: Must be one of [today, tomorrow, m-s, every *, month / day, etc]. For complete
        list see the expression_lists in handler objects in date_generator.py
        :return: list of Task
        """
        assert type(text) is str
        assert type(label) is str
        assert type(project) is str
        assert type(date_expression) is str
        try:
            task_list = self.tasks.add(text, label, project, date_expression)
            if len(task_list) == 1:
                self.logger.info(f"Added task #{task_list[0].index}")
            else:
                self.logger.info(f"Added {len(task_list)} tasks")
            return task_list
        except AttributeError as ex:
            self.logger.info(ex)

    def display_invalid_index_error(self, index: int):
        assert type(index) is int
        self.logger.info(f"Provided index {index} is invalid")

    def delete_tasks(self, index_tuple: tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.tasks.delete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def complete_tasks(self, index_tuple: tuple) -> list:
        """
        Changes the completed status in the DueDate object
        :param index_tuple: int tuple
        :return: list
        """
        assert type(index_tuple) is tuple

        results = list()
        for index in index_tuple:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                if task.is_completed() is False:
                    results.append(self.tasks.complete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def undelete_tasks(self, index_tuple: tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.tasks.undelete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def reset_tasks(self, index_tuple: tuple) -> list:
        """
        Copies tasks from the past into the present.
        :param index_tuple: int tuple
        :return: list
        """
        assert type(index_tuple) is tuple

        results = list()
        for index in index_tuple:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.tasks.reset(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def list_all_tasks(self, display_all: bool = False) -> List[Task]:
        if display_all:
            task_list = self.tasks.get_object_list()
        else:
            task_list = [task for task in self.tasks.get_object_list() if not task.deleted]
        return self.display_tasks(task_list)
