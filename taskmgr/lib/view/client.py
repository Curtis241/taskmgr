from abc import abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.tasks import TaskKeyError, DueDateError
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.client_args import *


class Client:
    """
    Base client facade that that provides access to all the application features.
    It integrates the import/export, tasks, snapshot, common variables,
    and date generator classes. It also makes it possible to support additional clients.
    Only the console client is supported, but a rest api could also extend this class.
    """
    logger = AppLogger("client").get_logger()

    def __init__(self, db_manager):
        assert isinstance(db_manager, DatabaseManager)

        self.tasks = db_manager.get_tasks_model()
        self.snapshots = db_manager.get_snapshots_model()
        self.__date_generator = DateGenerator()
        self.__variables = CommonVariables()

    @abstractmethod
    def display_tasks(self, task_list: list): pass

    @abstractmethod
    def display_snapshots(self, snapshot_list: list): pass

    @abstractmethod
    def display_invalid_index_error(self, index: int): pass

    @abstractmethod
    def display_due_date_error(self, message: str): pass

    def get_task(self, args: GetArg) -> List[Task]:
        task = self.tasks.get_task_by_index(args.index)
        return self.display_tasks([task])

    def filter_tasks_by_today(self) -> List[Task]:
        date_string = Today().to_date_string()
        task_list = self.tasks.get_tasks_by_date(date_string)
        return self.display_tasks(task_list)

    def filter_tasks_by_due_date(self, args: DueDateArgs) -> List[Task]:
        task_list = self.tasks.get_tasks_by_date(args.due_date)
        return self.display_tasks(task_list)

    def filter_tasks_by_due_date_range(self, args: DueDateRangeArgs) -> List[Task]:
        task_list = self.tasks.get_tasks_within_date_range(args.min_date, args.max_date, args.page)
        return self.display_tasks(task_list)

    def filter_tasks_by_status(self, args: StatusArgs) -> List[Task]:
        assert args.status in ["incomplete", "complete"]
        if args.status == "incomplete":
            task_list = self.tasks.get_tasks_by_status(False, args.page)
        else:
            task_list = self.tasks.get_tasks_by_status(True, args.page)
        return self.display_tasks(task_list)

    def filter_tasks_by_project(self, args: ProjectArgs) -> List[Task]:
        task_list = self.tasks.get_tasks_by_project(args.project, args.page)
        return self.display_tasks(task_list)

    def filter_tasks_by_label(self, args: LabelArgs) -> List[Task]:
        task_list = self.tasks.get_tasks_by_label(args.label, args.page)
        return self.display_tasks(task_list)

    def filter_tasks_by_name(self, args: NameArgs) -> List[Task]:
        task_list = self.tasks.get_tasks_containing_name(args.name, args.page)
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

    def count_all_tasks(self, page: int = 0) -> List[Snapshot]:
        snapshot_list = self.snapshots.get_all(page)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def count_tasks_by_due_date_range(self, args: DueDateRangeArgs) -> List[Snapshot]:
        snapshot_list = self.snapshots.get_by_due_date_range(args.min_date, args.max_date, args.page)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def count_tasks_by_due_date(self, args: DueDateArgs) -> List[Snapshot]:
        snapshot_list = self.snapshots.get_by_due_date(args.due_date)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def count_tasks_by_project(self, args: ProjectArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_by_project(args.project, args.page)
        snapshot_list = self.snapshots.build_snapshot_list(task_list)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def count_tasks_by_label(self, args: LabelArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_by_label(args.label, args.page)
        snapshot_list = self.snapshots.build_snapshot_list(task_list)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def count_tasks_by_name(self, args: NameArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_containing_name(args.name, args.page)
        snapshot_list = self.snapshots.build_snapshot_list(task_list)
        self.display_snapshots(snapshot_list)
        return snapshot_list

    def reschedule_tasks(self):
        task_list = self.tasks.reschedule()
        self.snapshots.rebuild(task_list)

    def remove_all_tasks(self):
        self.tasks.clear()
        self.snapshots.clear()

    def set_default_variables(self, **kwargs):
        """
        Sets the defaults variables to the variables.ini file.
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

    def group_edit(self, args: GroupEditArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            try:
                task = self.tasks.edit(index, None, args.label,
                                       args.project, args.due_date, args.time_spent)
                task_list.append(task)
            except TaskKeyError:
                self.display_invalid_index_error(index)

        self.display_tasks(task_list)
        self.snapshots.update(task_list)
        return task_list

    def edit(self, args: EditArgs) -> List[Task]:
        """
        Edits an existing task by replacing string values. None are allowed
        and handled by the Task object.
        :param args: EditArgs
        :return: List of Task
        """
        try:
            task = self.tasks.edit(args.index, args.name, args.label,
                                   args.project, args.due_date, args.time_spent)

            task_list = [task]
            self.display_tasks(task_list)
            self.snapshots.update(task_list)
            return task_list
        except TaskKeyError:
            self.display_invalid_index_error(args.index)

    def add(self, args: AddArgs) -> List[Task]:
        try:
            task_list = self.tasks.add(args.name, args.label, args.project, args.due_date)
            self.display_tasks(task_list)
            self.snapshots.update(task_list)
            return task_list
        except DueDateError as ex:
            self.display_due_date_error(str(ex))

    def delete(self, args: DeleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.delete(task))
            else:
                self.display_invalid_index_error(index)

        self.display_tasks(task_list)
        self.snapshots.update(task_list)
        return task_list

    def complete(self, args: CompleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                if args.time_spent > 0:
                    task.time_spent = args.time_spent
                task_list.append(self.tasks.complete(task))
            else:
                self.display_invalid_index_error(index)

        self.display_tasks(task_list)
        self.snapshots.update(task_list)
        return task_list

    def undelete(self, args: UndeleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.undelete(task))
            else:
                self.display_invalid_index_error(index)

        self.display_tasks(task_list)
        self.snapshots.update(task_list)
        return task_list

    def reset(self, args: ResetArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.reset(task))
            else:
                self.display_invalid_index_error(index)

        self.display_tasks(task_list)
        self.snapshots.update(task_list)
        return task_list

    def list_all_tasks(self, args: ListArgs) -> List[Task]:
        if args.all:
            task_list = self.tasks.get_task_list(args.page)
        else:
            task_list = [task for task in self.tasks.get_task_list(args.page) if not task.deleted]
        return self.display_tasks(task_list)
