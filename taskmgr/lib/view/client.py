from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, GoogleTasksExporter
from taskmgr.lib.variables import CommonVariables


class Client:
    """
    Base client facade that that provides access to all the application features. It integrates the import/export, tasks,
    snapshot, common variables, and date generator classes. It also makes it possible to support additional clients.
    Currently only the console client is supported, but a rest api could also extend this class.
    """
    logger = AppLogger("client").get_logger()

    def __init__(self, db_manager):
        assert isinstance(db_manager, DatabaseManager)
        self.__tasks = db_manager.get_tasks_model()
        self.__snapshots = db_manager.get_snapshots_model()
        self.__date_generator = DateGenerator()
        self.__variables = CommonVariables()

    def get_unique_label_list(self) -> List[str]:
        """Returns a list of labels from the tasks."""
        return list(self.__tasks.get_label_set())

    def get_unique_project_list(self) -> List[str]:
        """Returns list of project names from the tasks. """
        return list(self.__tasks.get_project_set())

    def get_tasks_by_project(self, project: str) -> List[Task]:
        """Returns list of tasks that match the provided project name. """
        assert type(project) is str
        return self.__tasks.get_tasks_by_project(project)

    def get_tasks_by_label(self, label: str) -> List[Task]:
        """Returns list of tasks that match the provided label. """
        assert type(label) is str
        return self.__tasks.get_tasks_by_label(label)

    def get_tasks_by_text(self, text: str) -> List[Task]:
        """Returns list of tasks that contain the provided text string. """
        assert type(text) is str
        return self.__tasks.get_tasks_containing_text(text)

    def get_tasks_by_status(self, is_completed: bool) -> List[Task]:
        """Returns list of tasks that are either completed/incomplete"""
        assert type(is_completed) is bool
        return self.__tasks.get_tasks_by_status(is_completed)

    def get_task_list(self) -> List[Task]:
        """Returns all tasks"""
        return self.__tasks.get_object_list()

    def get_snapshot_list(self) -> List[Snapshot]:
        return self.__snapshots.get_snapshot_list()

    def get_tasks_for_today(self) -> List[Task]:
        return self.__tasks.get_tasks_by_date(Today().to_date_string())

    def get_tasks_by_date(self, date_string: str):
        assert type(date_string) is str
        return self.__tasks.get_tasks_by_date(date_string)

    def get_tasks_within_date_range(self, min_date_string: str, max_date_string: str) -> List[Task]:
        assert type(min_date_string) is str
        assert type(max_date_string) is str
        return self.__tasks.get_tasks_within_date_range(min_date_string, max_date_string)

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
        return self.__tasks.add(text, label, project, date_expression)

    def delete_tasks_by_index(self, index_tuple: tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.delete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def delete_tasks_by_text(self, text: str) -> list:
        assert type(text) is str
        results = list()
        task_list = self.__tasks.get_tasks_matching_text(text)
        for task in task_list:
            results.append(self.__tasks.delete(task.unique_id))
        return results

    def edit_task(self, index: int, text: str, project: str, label: str, date_expression: str) -> Task:
        """
        Edits an existing task by replacing string values. None are allowed
        and handled by the Task object.
        :param index: integer starting at 0
        :param text: text string describing the task
        :param project: project name of the task
        :param label: label name of the task
        :param date_expression: Must be one of [today, tomorrow, m-s, every *, month / day, etc]. For complete
        list see the expression_lists in handler objects in date_generator.py
        :return: Task
        """
        assert type(index) is int
        assert type(text) is str
        assert type(project) is str
        assert type(label) is str
        assert type(date_expression) is str

        task = self.__tasks.get_task_by_index(index)
        if task is None:
            self.display_invalid_index_error(index)

        if self.__date_generator.validate_input(date_expression) is False:
            self.logger.info(f"Provided due date {date_expression} is invalid")

        return self.__tasks.edit(task.unique_id, text, label, project, date_expression)

    def complete_tasks(self, index_tuple: tuple) -> list:
        """
        Changes the completed status in the DueDate object
        :param index_tuple: int tuple
        :return: list
        """
        assert type(index_tuple) is tuple

        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                if task.is_completed() is False:
                    results.append(self.__tasks.complete(task.unique_id))
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
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.reset(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def reschedule_tasks(self, today=Today()):
        self.__tasks.reschedule(today)

    def remove_all_tasks(self):
        self.__tasks.clear()

    def set_defaults(self, variable_dict: dict):
        """
        Sets the defaults variables to the variables.ini file.
        :param variable_dict: Contains key value pairs matching the
        properties in Variables class
        :return: None
        """
        assert type(variable_dict) is dict

        for key, value in variable_dict.items():
            if hasattr(self.__variables, key):
                setattr(self.__variables, key, value)

    @staticmethod
    def get_duration(start_datetime):
        """
        Gets a formatted time string using the provided datetime object
        :param start_datetime:
        :return: time string
        """
        end_datetime = datetime.now()
        total_seconds = (end_datetime - start_datetime).total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}m:{:02}s'.format(int(minutes), int(seconds))

    def count_tasks(self, task_list) -> List[Snapshot]:
        assert type(task_list) is list

        snapshot_list = list()
        for index, project in enumerate(self.__tasks.unique("project", task_list), start=1):
            tasks = self.__tasks.get_list_by_type("project", project, task_list)
            snapshot = self.__snapshots.count_tasks(project, tasks)
            snapshot.index = index
            snapshot_list.append(snapshot)

        return snapshot_list

    def save_snapshots(self, snapshots: list):
        for snapshot in snapshots:
            snapshot.index = 0
            self.__snapshots.add(snapshot)

    def import_tasks(self, google_tasks_importer, project: str):
        """
        Imports tasks from the Google Tasks service
        :param google_tasks_importer: GoogleTasksImporter class
        :param project: Local task project
        :return: None
        """
        assert isinstance(google_tasks_importer, GoogleTasksImporter)
        assert type(project) is str

        start_datetime = datetime.now()
        self.logger.info(f"Starting import")
        import_task_list = google_tasks_importer.convert_to_task_list(project)
        self.logger.info(f"Retrieved {len(import_task_list)} tasks from service")
        sync_results = google_tasks_importer.import_tasks(import_task_list)
        self.logger.info(f"Import summary: {sync_results.get_summary()}")

        self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")

    def export_tasks(self, google_tasks_exporter, project: str):
        """
        Exports tasks to the Google Tasks service
        :param google_tasks_exporter: GoogleTasksExporter class
        :param project: Local task project
        :return: None
        """
        assert isinstance(google_tasks_exporter, GoogleTasksExporter)
        assert type(project) is str

        start_datetime = datetime.now()

        self.logger.info(f"Starting export")
        self.logger.info(f"Preparing tasks for export")
        gtasks_list = google_tasks_exporter.convert_to_gtasklist(project)
        self.logger.info(f"Exporting tasks to service")
        sync_results = google_tasks_exporter.export_tasks(gtasks_list)
        self.logger.info(f"Export summary: {sync_results.get_summary()}")

        self.logger.info(f"Export complete: Duration: {self.get_duration(start_datetime)}")

    def display_invalid_index_error(self, index: int):
        assert type(index) is int
        self.logger.info(f"Provided index {index} is invalid")

    @staticmethod
    def get_variables_list():
        return dict(CommonVariables()).items()
