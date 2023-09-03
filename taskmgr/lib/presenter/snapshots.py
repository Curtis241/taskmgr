from typing import List

from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.database.snapshots_db import SnapshotsDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.presenter.time_cards import TimeCards


class Snapshots:
    logger = AppLogger("snapshots").get_logger()

    def __init__(self, tasks: Tasks, time_cards: TimeCards, database: SnapshotsDatabase):
        assert isinstance(tasks, Tasks)
        assert isinstance(database, SnapshotsDatabase)
        assert isinstance(time_cards, TimeCards)

        self.__tasks = tasks
        self.__time_cards = time_cards
        self.__db = database
        self.__date_generator = DateTimeGenerator()

    def build_snapshot(self, task_list: List[Task],
                       time_card_list: List[TimeCard] = None) -> Snapshot:
        """
        Creates a single snapshot when all tasks have the same due_date.
        """
        snapshot = Snapshot()
        if len(task_list) > 0:
            for task in task_list:
                if task.deleted:
                    snapshot.delete_count += 1

                if task.completed is True:
                    snapshot.complete_count += 1
                else:
                    snapshot.incomplete_count += 1

                snapshot.total_time = snapshot.total_time + task.time_spent
                snapshot.task_count = len(task_list)
                snapshot.due_date = task.due_date
                snapshot.due_date_timestamp = task.due_date_timestamp

        if time_card_list is not None and len(time_card_list) > 0:
            snapshot.actual_time = self.__time_cards.sum_total_times(time_card_list)

        return snapshot

    def summarize_tasks(self, task_list: List[Task]) -> List[Snapshot]:
        """
        Creates one snapshot for each due_date. Only
        the tasks provided will be summarized and are not expected to be
        persisted to redis. Typically used for analyzing tasks that are
        filtered based on name, label, or project.
        """
        snapshot_list = list()
        if len(task_list) > 0:
            snapshot_list = []

            due_date_list = sorted(list(set([task.due_date for task in task_list])))
            for due_date in due_date_list:
                filtered_list = [task for task in task_list if task.due_date == due_date]
                snapshot = self.build_snapshot(filtered_list)
                snapshot_list.append(snapshot)

        return snapshot_list

    def summarize_and_fill(self, task_list: List[Task]) -> List[Snapshot]:
        """
        Creates one snapshot for each due_date. The due_date is used
        to fetch all tasks for each day. Only one task is needed from
        each due_date because other tasks may already exist.
        """
        snapshot_list = list()
        if len(task_list) > 0:
            snapshot_list = []
            due_date_list = list(set([task.due_date for task in task_list]))
            for index, due_date_string in enumerate(due_date_list, start=1):
                task_query_result = self.__tasks.get_tasks_by_date(due_date_string)
                time_card_query_result = self.__time_cards.get_time_cards_by_date(due_date_string)
                snapshot = self.build_snapshot(task_query_result.to_list(),
                                               time_card_query_result.to_list())
                snapshot_list.append(snapshot)

        return snapshot_list

    def update(self, task_list: List[Task]):
        if task_list is not None:
            snapshot_list = self.summarize_and_fill(task_list)
            for snapshot in snapshot_list:
                existing_snapshot = self.__db.get_object("due_date_timestamp", snapshot.due_date_timestamp)
                if existing_snapshot is None:
                    self.__db.append_object(snapshot)
                else:
                    existing_snapshot.update(snapshot)
                    self.__db.replace_object(existing_snapshot)

    def rebuild(self):
        result = self.__tasks.get_all()
        snapshot_list = self.summarize_and_fill(result.to_list())
        self.__db.append_objects(snapshot_list)

    def get_all(self, page: int = 0) -> QueryResult:
        self.__db.set_page_number(page)
        return self.__db.get_all()

    def get_by_due_date_range(self, min_date: str, max_date: str, page: int = 0) -> QueryResult:
        assert type(min_date) is str
        assert type(max_date) is str

        min_date = self.__date_generator.get_day(min_date)
        max_date = self.__date_generator.get_day(max_date)

        if min_date is not None and max_date is not None:
            self.__db.set_page_number(page)
            result = self.__db.get_selected("due_date_timestamp",
                                            min_date.to_date_timestamp(),
                                            max_date.to_date_timestamp())
            return result
        else:
            return QueryResult()

    def get_by_due_date(self, date_expression: str) -> QueryResult:
        snapshot_list = list()
        days = self.__date_generator.get_days(date_expression)
        for day in days:
            snapshot = self.__db.get_object("due_date_timestamp", day.to_date_timestamp())
            if snapshot is not None:
                snapshot_list.append(snapshot)

        return QueryResult(snapshot_list)

    def clear(self):
        self.__db.clear()