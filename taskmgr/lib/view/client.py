from abc import abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, GoogleTasksExporter, CsvFileImporter
from taskmgr.lib.variables import CommonVariables


class Client:
    """
    Base client facade that that provides access to all the application features. It integrates the import/export, tasks,
    snapshot, common variables, and date generator classes. It also makes it possible to support additional clients.
    Currently only the console client is supported, but a rest api could also extend this class.
    """
    logger = AppLogger("client").get_logger()

    def __init__(self, db_manager, file_manager):
        assert isinstance(db_manager, DatabaseManager)
        assert isinstance(file_manager, FileManager)

        self.__file_manager = file_manager
        self.__tasks = db_manager.get_tasks_model()
        self.__snapshots = db_manager.get_snapshots_model()
        self.__date_generator = DateGenerator()
        self.__variables = CommonVariables()

    @abstractmethod
    def display_tasks(self, task_list: list, kwargs): pass

    @abstractmethod
    def display_snapshots(self, snapshot_list: list, kwargs): pass

    def list_all_tasks(self, **kwargs) -> List[Task]:
        task_list = self.__tasks.get_object_list()
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_today(self, **kwargs) -> List[Task]:
        date_string = Today().to_date_string()
        task_list = self.__tasks.get_tasks_by_date(date_string)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_due_date(self, **kwargs) -> List[Task]:
        date_string = kwargs.get("date")
        task_list = self.__tasks.get_tasks_by_date(date_string)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_due_date_range(self, **kwargs) -> List[Task]:
        min_date_string = kwargs.get("min_date")
        max_date_string = kwargs.get("max_date")
        task_list = self.__tasks.get_tasks_within_date_range(min_date_string, max_date_string)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_status(self, **kwargs) -> List[Task]:
        status_type = kwargs.get("status")
        if status_type == "incomplete":
            task_list = self.__tasks.get_tasks_by_status(is_completed=False)
        else:
            task_list = self.__tasks.get_tasks_by_status(is_completed=True)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_project(self, **kwargs) -> List[Task]:
        project = kwargs.get("project")
        task_list = self.__tasks.get_tasks_by_project(project)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_label(self, **kwargs) -> List[Task]:
        label = kwargs.get("label")
        task_list = self.__tasks.get_tasks_by_label(label)
        return self.display_tasks(task_list, kwargs)

    def filter_tasks_by_text(self, **kwargs) -> List[Task]:
        text = str(kwargs.get("text"))
        task_list = self.__tasks.get_tasks_containing_text(text)
        return self.display_tasks(task_list, kwargs)

    def group_tasks_by_project(self, **kwargs) -> List[Task]:
        task_list = list()
        for project in self.get_unique_project_list():
            for task in self.__tasks.get_tasks_by_project(project):
                task_list.append(task)
        return self.display_tasks(task_list, kwargs)

    def group_tasks_by_due_date(self, **kwargs) -> List[Task]:
        task_list = list()
        for due_date_string in self.get_unique_due_date_list():
            for task in self.__tasks.get_tasks_by_date(due_date_string):
                task_list.append(task)
        return self.display_tasks(task_list, kwargs)

    def group_tasks_by_label(self, **kwargs) -> List[Task]:
        task_list = list()
        for label in self.get_unique_label_list():
            for task in self.__tasks.get_tasks_by_label(label):
                task_list.append(task)
        return self.display_tasks(task_list, kwargs)

    def set_default_variables(self, **kwargs):
        self.set_defaults(kwargs)

    def get_unique_label_list(self) -> List[str]:
        """Returns a list of labels from the tasks."""
        return list(self.__tasks.get_label_set())

    def get_unique_project_list(self) -> List[str]:
        """Returns list of project names from the tasks. """
        return list(self.__tasks.get_project_set())

    def get_unique_due_date_list(self) -> List[str]:
        """Returns list of due_date strings from the tasks."""
        return list(sorted(self.__tasks.get_due_date_set()))

    def get_snapshot_list(self) -> List[Snapshot]:
        return self.__snapshots.get_snapshot_list()

    def count_all_tasks(self, **kwargs) -> List[Snapshot]:
        if kwargs.get("due_date"):
            task_list = self.__tasks.get_object_list()
            snapshot_list = self.count_tasks_by_date(task_list)
        else:
            task_list = self.__tasks.get_object_list()
            snapshot_list = self.count_total_tasks("all tasks", task_list)
        return self.display_snapshots(snapshot_list, kwargs)

    def count_tasks_by_due_date_range(self, **kwargs) -> List[Snapshot]:
        min_date_string = kwargs.get("min_date")
        max_date_string = kwargs.get("max_date")

        task_list = self.__tasks.get_tasks_within_date_range(min_date_string, max_date_string)
        context = f"min_due_date: {min_date_string} to max_due_date: {max_date_string}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, kwargs)

    def count_tasks_by_label(self, **kwargs) -> List[Snapshot]:
        label = kwargs.get("label")
        task_list = self.__tasks.get_tasks_by_label(label)
        context = f"label: {label}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, kwargs)

    def count_tasks_by_due_date(self, **kwargs) -> List[Snapshot]:
        date_string = kwargs.get("date")
        task_list = self.__tasks.get_tasks_by_date(date_string)
        context = f"due_date: {date_string}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, kwargs)

    def count_tasks_by_today(self) -> List[Snapshot]:
        date_string = Today().to_date_string()
        task_list = self.__tasks.get_tasks_by_date(date_string)
        context = f"due_date: {date_string}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, {})

    def count_tasks_by_project(self, **kwargs) -> List[Snapshot]:
        project = kwargs.get("project")
        task_list = self.__tasks.get_tasks_by_project(project)
        context = f"project: {project}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, kwargs)

    def count_tasks_by_status(self, **kwargs):
        status_type = kwargs.get("status")
        if status_type == "complete":
            task_list = self.__tasks.get_tasks_by_status(is_completed=True)
        else:
            task_list = self.__tasks.get_tasks_by_status(is_completed=False)

        context = f"status: {status_type}"
        snapshot_list = self.count_total_tasks(context, task_list)
        return self.display_snapshots(snapshot_list, kwargs)

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
        task_list = self.__tasks.add(text, label, project, date_expression)
        if len(task_list) > 0:
            self.logger.info(f"Added task {task_list[0].index}")
        return task_list

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

    def delete_tasks(self, index_tuple: tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.delete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def undelete_tasks(self, index_tuple: tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.undelete(task.unique_id))
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

    def count_total_tasks(self, context, task_list) -> List[Snapshot]:
        assert type(context) is str
        assert type(task_list) is list

        snapshot_list = list()
        for index, project in enumerate(self.__tasks.unique("project", task_list), start=1):
            task_list = self.__tasks.get_list_by_type("project", project, task_list)
            snapshot = self.__snapshots.total_count(context, project, task_list)
            snapshot.index = index
            snapshot_list.append(snapshot)
        return snapshot_list

    def count_tasks_by_date(self, task_list) -> List[Snapshot]:
        assert type(task_list) is list

        snapshot_list = list()
        for index, due_date_string in enumerate(self.get_unique_due_date_list(), start=1):
            task_list = self.__tasks.get_tasks_by_date(due_date_string)
            context = f"due_date: {due_date_string}"
            snapshot_list.extend(self.count_total_tasks(context, task_list))
        return snapshot_list

    def save_snapshots(self, snapshot_list: list):
        for snapshot in snapshot_list:
            snapshot.index = 0
            self.__snapshots.add(snapshot)

    def save_tasks_to_file(self, task_list: list):
        self.__file_manager.save_tasks(task_list)

    def save_snapshots_to_file(self, snapshot_list: list):
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

    def download_tasks(self, google_tasks_importer: GoogleTasksImporter, project: str):
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
        import_task_list = google_tasks_importer.convert(project)
        self.logger.info(f"Retrieved {len(import_task_list)} tasks from service")
        sync_results = google_tasks_importer.import_tasks(import_task_list)
        self.logger.info(f"Import summary: {sync_results.get_summary()}")

        self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")

    def upload_tasks(self, google_tasks_exporter: GoogleTasksExporter, project_name: str):
        """
        Exports tasks to the Google Tasks service
        :param google_tasks_exporter: GoogleTasksExporter class
        :param project_name: Local task project
        :return: None
        """
        assert isinstance(google_tasks_exporter, GoogleTasksExporter)
        assert type(project_name) is str

        start_datetime = datetime.now()

        self.logger.info(f"Starting export")
        if not google_tasks_exporter.project_exist(project_name):
            self.logger.info(f"Preparing tasks for export")
            local_project_list = google_tasks_exporter.convert(project_name)
            self.logger.info(f"Exporting tasks to service")
            sync_results = google_tasks_exporter.export_tasks(local_project_list)
            self.logger.info(f"Export summary: {sync_results.get_summary()}")

            self.logger.info(f"Export complete: Duration: {self.get_duration(start_datetime)}")
        else:
            self.logger.info("ERROR: Cannot overwrite tasks in project")

    def display_invalid_index_error(self, index: int):
        assert type(index) is int
        self.logger.info(f"Provided index {index} is invalid")

    @staticmethod
    def get_variables_list():
        return dict(CommonVariables()).items()
