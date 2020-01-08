from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import Today, DateGenerator
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables


class Client:
    """
    Base client class to provide generic features for additional clients (ie. rest api)
    """
    logger = AppLogger("client").get_logger()

    def __init__(self, tasks, snapshots):
        assert type(tasks) is Tasks
        assert type(snapshots) is Snapshots
        self.__tasks = tasks
        self.__snapshots = snapshots
        self.date_generator = DateGenerator()

    def get_unique_label_list(self):
        """Returns a list of labels from the tasks. Wrapped so method can be overridden."""
        return list(self.__tasks.unique(SortType.Label))

    def get_unique_project_list(self):
        """Returns list of project names from the tasks. Wrapped so method can be overridden."""
        return list(self.__tasks.unique(SortType.Project))

    def get_tasks_by_project(self, project, include_deleted=False):
        """Returns list of tasks that match the provided project name. Wrapped so method can be overridden."""
        assert type(project) is str
        return self.__tasks.get_list_by_type(SortType.Project, project, include_deleted)

    def get_tasks_by_label(self, label):
        """Returns list of tasks that match the provided label. Wrapped so method can be overridden."""
        assert type(label) is str
        return self.__tasks.get_list_by_type(SortType.Label, label)

    def get_tasks_by_text(self, text):
        """Returns list of tasks that match the provided text string. Wrapped so method can be overridden."""
        assert type(text) is str
        return self.__tasks.get_list_by_type(SortType.Text, text)

    def get_task_list(self):
        """Returns list of tasks that are not deleted. Wrapped so method can be overridden."""
        return self.__tasks.get_filtered_list()

    def add_task(self, text, label, project, date_expression) -> Task:
        """
        Adds a task
        :param text: text string describing the task
        :param label: label for the task
        :param project: project name for the task
        :param date_expression: Must be one of [today, tomorrow, m-s, every *, month / day, etc]. For complete
        list see the expression_lists in handler objects in date_generator.py
        :return: Task
        """
        assert type(text) is str
        assert type(label) is str
        assert type(project) is str
        assert type(date_expression) is str
        if self.date_generator.validate_input(date_expression):
            task = Task(text)
            task.label = label
            task.project = project
            task.date_expression = date_expression
            self.__tasks.add(task)
            return task
        else:
            self.display_invalid_due_date_error(date_expression)

    def delete_tasks(self, index_tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.delete(task.unique_id))
            else:
                self.display_invalid_index_error(index)
        return results

    def edit_task(self, index, text, project, label, date_expression) -> Task:
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
        assert type(date_expression) is str
        task = self.__tasks.get_task_by_index(index)
        if task is None:
            self.display_invalid_index_error(index)

        if self.date_generator.validate_input(date_expression) is False:
            self.display_invalid_due_date_error(date_expression)

        return self.__tasks.edit(task.unique_id, text, label, project, date_expression)

    def complete_tasks(self, index_tuple) -> list:
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

    def reset_tasks(self, index_tuple) -> list:
        """
        Copies tasks from the past into the present.
        :param index_tuple: int tuple
        :return: list
        """
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

    @staticmethod
    def set_defaults(variable_dict):
        """
        Sets the defaults variables to the variables.ini file.
        :param variable_dict: Contains key value pairs matching the
        properties in Variables class
        :return: None
        """
        assert type(variable_dict) is dict
        variables = CommonVariables()
        for key, value in variable_dict.items():
            if hasattr(variables, key):
                setattr(variables, key, value)

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

    def count_tasks(self) -> List[Snapshot]:
        return self.__snapshots.count_tasks(self.__tasks)

    def export_snapshots(self):
        pass

    def import_snapshots(self):
        pass

    def import_tasks(self, google_tasks_importer, project):
        """
        Imports tasks from the Google Tasks service
        :param google_tasks_importer: GoogleTasksImporter class
        :param project: Local task project
        :return: None
        """
        start_datetime = datetime.now()

        self.logger.info(f"Starting import")
        import_task_list = google_tasks_importer.convert_to_task_list(project)
        self.logger.info(f"Retrieved {len(import_task_list)} tasks from service")
        sync_results = google_tasks_importer.import_tasks(import_task_list)
        self.logger.info(f"Import summary: {sync_results.get_summary()}")

        self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")

    def export_tasks(self, google_tasks_exporter, project):
        """
        Exports tasks to the Google Tasks service
        :param google_tasks_exporter: GoogleTasksExporter class
        :param project: Local task project
        :return: None
        """
        start_datetime = datetime.now()

        self.logger.info(f"Starting export")
        self.logger.info(f"Preparing tasks for export")
        gtasks_list = google_tasks_exporter.convert_to_gtasklist(project)
        self.logger.info(f"Exporting tasks to service")
        sync_results = google_tasks_exporter.export_tasks(gtasks_list)
        self.logger.info(f"Export summary: {sync_results.get_summary()}")

        self.logger.info(f"Export complete: Duration: {self.get_duration(start_datetime)}")

    def display_invalid_index_error(self, index):
        self.logger.info(f"Provided index {index} is invalid")

    def display_invalid_due_date_error(self, date_expression):
        self.logger.info(f"Provided due date {date_expression} is invalid")
