from abc import abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import TaskKeyError
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

        self.tasks = db_manager.get_tasks_model()
        self.__date_generator = DateGenerator()
        self.__variables = CommonVariables()

    @abstractmethod
    def display_tasks(self, task_list: list): pass

    @abstractmethod
    def display_snapshots(self, snapshots: Snapshots, **kwargs): pass

    @abstractmethod
    def display_invalid_index_error(self, index: int): pass

    def edit_task(self, index: int, text: str, label: str, project: str, date_expression: str) -> List[Task]:
        """
        Edits an existing task by replacing string values. None are allowed
        and handled by the Task object.
        :param index: integer starting at 0
        :param text: text string describing the task
        :param label: label name of the task
        :param project: project name of the task
        :param date_expression: Must be one of [today, tomorrow, m-s, every *, month / day, etc].
        :return: Task
        """
        assert type(index) is int
        assert type(text) is str
        assert type(project) is str
        assert type(label) is str
        assert type(date_expression) is str

        try:
            if self.__date_generator.validate_input(date_expression) is False:
                self.logger.info(f"Provided due date {date_expression} is invalid")
            else:
                task = self.tasks.edit(index, text, label, project, date_expression)
                return self.display_tasks([task])
        except TaskKeyError:
            self.display_invalid_index_error(index)

    def get_task(self, task_index: int) -> List[Task]:
        task = self.tasks.get_task_by_index(int(task_index))
        return self.display_tasks([task])

    def filter_tasks_by_today(self) -> List[Task]:
        date_string = Today().to_date_string()
        task_list = self.tasks.get_tasks_by_date(date_string)
        return self.display_tasks(task_list)

    def filter_tasks_by_due_date(self, date_string: str) -> List[Task]:
        task_list = self.tasks.get_tasks_by_date(date_string)
        return self.display_tasks(task_list)

    def filter_tasks_by_due_date_range(self, min_date: str, max_date: str) -> List[Task]:
        task_list = self.tasks.get_tasks_within_date_range(min_date, max_date)
        return self.display_tasks(task_list)

    def filter_tasks_by_status(self, status: str) -> List[Task]:
        assert status in ["incomplete", "complete"]
        if status == "incomplete":
            task_list = self.tasks.get_tasks_by_status(is_completed=False)
        else:
            task_list = self.tasks.get_tasks_by_status(is_completed=True)
        return self.display_tasks(task_list)

    def filter_tasks_by_project(self, project: str) -> List[Task]:
        assert type(project) is str
        task_list = self.tasks.get_tasks_by_project(project)
        return self.display_tasks(task_list)

    def filter_tasks_by_label(self, label: str) -> List[Task]:
        assert type(label) is str
        task_list = self.tasks.get_tasks_by_label(label)
        return self.display_tasks(task_list)

    def filter_tasks_by_text(self, text: str) -> List[Task]:
        assert type(text) is str
        task_list = self.tasks.get_tasks_containing_text(text)
        return self.display_tasks(task_list)

    def group_tasks_by_project(self) -> List[Task]:
        task_list = list()
        for project in self.get_unique_project_list():
            for task in self.tasks.get_tasks_by_project(project):
                task_list.append(task)
        return self.display_tasks(task_list)

    def group_tasks_by_due_date(self) -> List[Task]:
        task_list = list()
        for due_date_string in self.__get_unique_due_date_list():
            for task in self.tasks.get_tasks_by_date(due_date_string):
                task_list.append(task)
        return self.display_tasks(task_list)

    def group_tasks_by_label(self) -> List[Task]:
        task_list = list()
        for label in self.get_unique_label_list():
            for task in self.tasks.get_tasks_by_label(label):
                task_list.append(task)
        return self.display_tasks(task_list)

    def get_unique_label_list(self) -> List[str]:
        """Returns a list of labels from the tasks."""
        return self.tasks.get_label_list()

    def get_unique_project_list(self) -> List[str]:
        """Returns list of project names from the tasks. """
        return self.tasks.get_project_list()

    def __get_unique_due_date_list(self) -> List[str]:
        """Returns list of due_date strings from the tasks."""
        return self.tasks.get_due_date_list()

    def count_all_tasks(self, **kwargs) -> List[Snapshot]:
        snapshots = Snapshots(self.tasks)
        snapshots.count_all_tasks()
        return self.display_snapshots(snapshots, **kwargs)

    def count_tasks_by_due_date_range(self, min_date: str, max_date: str, **kwargs) -> List[Snapshot]:
        assert type(min_date) and type(max_date) is str

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_due_date_range(min_date, max_date)
        return self.display_snapshots(snapshots, **kwargs)

    def count_tasks_by_due_date(self, due_date: str, **kwargs) -> List[Snapshot]:
        assert type(due_date) is str

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_due_date(due_date)
        return self.display_snapshots(snapshots, **kwargs)

    def count_tasks_by_project(self, project_name: str, **kwargs) -> List[Snapshot]:
        assert type(project_name) is str

        snapshots = Snapshots(self.tasks)
        snapshots.count_tasks_by_project(project_name)
        return self.display_snapshots(snapshots, **kwargs)

    def reschedule_tasks(self, today=Today()):
        self.tasks.reschedule(today)

    def remove_all_tasks(self):
        self.tasks.clear()

    def set_default_variables(self, **kwargs):
        """
        Sets the defaults variables to the variables.ini file.
        :param variable_dict: Contains key value pairs matching the
        properties in Variables class
        :return: None
        """
        assert type(kwargs) is dict

        for key, value in kwargs.items():
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

    @staticmethod
    def get_variables_list():
        return dict(CommonVariables()).items()
