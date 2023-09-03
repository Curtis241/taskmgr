from abc import abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Today
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
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
        self.time_cards = db_manager.get_time_cards_model()
        self.__date_generator = DateTimeGenerator()
        self.__variables = CommonVariables()

    @abstractmethod
    def display_tasks(self, result: QueryResult):
        pass

    @abstractmethod
    def display_snapshots(self, result: QueryResult):
        pass

    @abstractmethod
    def display_time_cards(self, result: QueryResult):
        pass

    @abstractmethod
    def display_invalid_index_error(self, index: int):
        pass

    @abstractmethod
    def display_attribute_error(self, param: str, message: str):
        pass

    def get_task(self, args: GetArg) -> List[Task]:
        task = self.tasks.get_task_by_index(args.index)
        return self.display_tasks(QueryResult([task]))

    def filter_tasks_by_today(self) -> List[Task]:
        date_string = Today().to_date_string()
        result = self.tasks.get_tasks_by_date(date_string)
        return self.display_tasks(result)

    def filter_tasks_by_due_date(self, args: DueDateArgs) -> List[Task]:
        result = self.tasks.get_tasks_by_date(args.due_date)
        return self.display_tasks(result)

    def filter_tasks_by_due_date_range(self, args: DueDateRangeArgs) -> List[Task]:
        result = self.tasks.get_tasks_within_date_range(args.min_date, args.max_date, args.page)
        return self.display_tasks(result)

    def filter_tasks_by_status(self, args: StatusArgs) -> List[Task]:
        assert args.status in ["incomplete", "complete"]
        if args.status == "incomplete":
            result = self.tasks.get_tasks_by_status(False, args.page)
        else:
            result = self.tasks.get_tasks_by_status(True, args.page)
        return self.display_tasks(result)

    def filter_tasks_by_project(self, args: ProjectArgs) -> List[Task]:
        result = self.tasks.get_tasks_by_project(args.project, args.page)
        return self.display_tasks(result)

    def filter_tasks_by_label(self, args: LabelArgs) -> List[Task]:
        result = self.tasks.get_tasks_by_label(args.label, args.page)
        return self.display_tasks(result)

    def filter_tasks_by_name(self, args: NameArgs) -> List[Task]:
        result = self.tasks.get_tasks_containing_name(args.name, args.page)
        return self.display_tasks(result)

    def group_tasks_by_project(self) -> List[Task]:
        result = QueryResult()
        for project in self.get_unique_project_list():
            for task in self.tasks.get_tasks_by_project(project).to_list():
                result.append(task)
        return self.display_tasks(result)

    def group_tasks_by_due_date(self) -> List[Task]:
        result = QueryResult()
        for due_date_string in self.__get_unique_due_date_list():
            for task in self.tasks.get_tasks_by_date(due_date_string).to_list():
                result.append(task)
        return self.display_tasks(result)

    def group_tasks_by_label(self) -> List[Task]:
        result = QueryResult()
        for label in self.get_unique_label_list():
            for task in self.tasks.get_tasks_by_label(label).to_list():
                result.append(task)
        return self.display_tasks(result)

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
        result = self.snapshots.get_all(page)
        return self.display_snapshots(result)

    def count_tasks_by_due_date_range(self, args: DueDateRangeArgs) -> List[Snapshot]:
        result = self.snapshots.get_by_due_date_range(args.min_date, args.max_date, args.page)
        return self.display_snapshots(result)

    def count_tasks_by_due_date(self, args: DueDateArgs) -> List[Snapshot]:
        result = self.snapshots.get_by_due_date(args.due_date)
        return self.display_snapshots(result)

    def count_tasks_by_project(self, args: ProjectArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_by_project(args.project, args.page).to_list()
        snapshot_list = self.snapshots.summarize_tasks(task_list)
        return self.display_snapshots(QueryResult(snapshot_list))

    def count_tasks_by_label(self, args: LabelArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_by_label(args.label, args.page).to_list()
        snapshot_list = self.snapshots.summarize_tasks(task_list)
        return self.display_snapshots(QueryResult(snapshot_list))

    def count_tasks_by_name(self, args: NameArgs) -> List[Snapshot]:
        task_list = self.tasks.get_tasks_containing_name(args.name).to_list()
        snapshot_list = self.snapshots.summarize_tasks(task_list)
        return self.display_snapshots(QueryResult(snapshot_list))

    def reschedule_tasks(self):
        for task in self.tasks.reschedule():
            original_task, new_task = self.tasks.edit(index=task.index, date_expression=task.due_date)
            self.snapshots.update([original_task, new_task])

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
                _, new_task = self.tasks.edit(index, None, args.label,
                                              args.project, args.due_date, args.time_spent)
                task_list.append(new_task)
            except TaskKeyError:
                return self.display_invalid_index_error(index)

        self.snapshots.update(task_list)
        return self.display_tasks(QueryResult(task_list))

    def edit_task(self, args: EditArgs) -> List[Task]:
        """
        Edits an existing task by replacing string values. None are allowed
        and handled by the Task object.
        :param args: EditArgs
        :return: List of Task
        """
        try:
            original_task, new_task = self.tasks.edit(args.index, args.name, args.label,
                                                      args.project, args.due_date, args.time_spent)

            self.snapshots.update([original_task, new_task])
            return self.display_tasks(QueryResult([new_task]))
        except TaskKeyError:
            return self.display_invalid_index_error(args.index)

    def add_task(self, args: AddArgs) -> List[Task]:
        try:
            if not args.name:
                return self.display_attribute_error("name", f"Empty name parameter")
            else:
                task_list = self.tasks.add(args.name, args.label, args.project, args.due_date)
                self.snapshots.update(task_list)
                return self.display_tasks(QueryResult(task_list))
        except DueDateError as ex:
            return self.display_attribute_error("due_date", str(ex))

    def delete_task(self, args: DeleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.delete(task))
            else:
                return self.display_invalid_index_error(index)

        self.snapshots.update(task_list)
        return self.display_tasks(QueryResult(task_list))

    def complete_task(self, args: CompleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                if args.time_spent > 0:
                    task.time_spent = args.time_spent

                task_list.append(self.tasks.complete(task))
            else:
                return self.display_invalid_index_error(index)

        self.snapshots.update(task_list)
        return self.display_tasks(QueryResult(task_list))

    def undelete_task(self, args: UndeleteArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.undelete(task))
            else:
                return self.display_invalid_index_error(index)

        self.snapshots.update(task_list)
        return self.display_tasks(QueryResult(task_list))

    def reset_task(self, args: ResetArgs) -> List[Task]:
        task_list = list()
        for index in args.indexes:
            task = self.tasks.get_task_by_index(index)
            if task is not None:
                task_list.append(self.tasks.reset(task))
            else:
                return self.display_invalid_index_error(index)

        self.snapshots.update(task_list)
        return self.display_tasks(QueryResult(task_list))

    def list_all_tasks(self, args: ListArgs) -> List[Task]:
        if args.all:
            result = self.tasks.get_all(args.page)
        else:
            result = self.tasks.get_undeleted_tasks(args.page)
        return self.display_tasks(result)

    def clear_tasks(self):
        self.tasks.clear()


    # TimeCards
    def add_time_card(self, args: AddTimeCardArgs):
        try:
            time_card = self.time_cards.add(args.time_in, args.time_out, args.date)
            return self.display_time_cards(QueryResult([time_card]))
        except DueDateError as ex:
            return self.display_attribute_error("due_date", str(ex))

    def delete_time_card(self, args: DeleteArgs):
        time_card_list = list()
        for index in args.indexes:
            time_card = self.time_cards.get_time_card_by_index(index)
            if time_card is not None:
                time_card_list.append(self.time_cards.delete(time_card))
            else:
                return self.display_invalid_index_error(index)

        return self.display_time_cards(QueryResult(time_card_list))

    def undelete_time_card(self, args: UndeleteArgs) -> List[Task]:
        time_card_list = list()
        for index in args.indexes:
            time_card = self.time_cards.get_time_card_by_index(index)
            if time_card is not None:
                time_card_list.append(self.time_cards.undelete(time_card))
            else:
                return self.display_invalid_index_error(index)

        return self.display_time_cards(QueryResult(time_card_list))

    def edit_time_card(self, args: EditTimeCardArgs) -> List[TimeCard]:
        try:
            original_time_card, new_time_card = \
                self.time_cards.edit(args.index, args.time_in, args.time_out, args.date)

            return self.display_time_cards(QueryResult([new_time_card]))
        except TaskKeyError:
            return self.display_invalid_index_error(args.index)

    def list_all_time_cards(self, args: ListArgs) -> List[TimeCard]:
        if args.all:
            result = self.time_cards.get_all()
        else:
            result = self.time_cards.get_all(args.page)
        return self.display_time_cards(result)

    def filter_time_cards_by_date_range(self, args: DateRangeArgs) -> List[TimeCard]:
        result = self.time_cards.get_time_cards_within_date_range(args.min_date, args.max_date, args.page)
        return self.display_time_cards(result)

    def filter_time_cards_by_date(self, args: DateArgs) -> List[TimeCard]:
        result = self.time_cards.get_time_cards_by_date(args.date, add_total=True)
        return self.display_time_cards(result)

    def filter_time_cards_by_today(self) -> List[TimeCard]:
        date_string = Today().to_date_string()
        result = self.time_cards.get_time_cards_by_date(date_string, add_total=True)
        return self.display_time_cards(result)

    def clear_time_cards(self):
        self.time_cards.clear()

