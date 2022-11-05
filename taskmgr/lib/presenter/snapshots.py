from typing import List

from taskmgr.lib.database.snapshots_db import SnapshotsDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.presenter.tasks import Tasks


class Snapshots:
    logger = AppLogger("snapshots").get_logger()

    def __init__(self, tasks: Tasks, database: SnapshotsDatabase):
        assert isinstance(tasks, Tasks)
        assert isinstance(database, SnapshotsDatabase)

        self.__tasks = tasks
        self.__db = database
        self.__date_generator = DateGenerator()

    @staticmethod
    def build_snapshot(task_list: List[Task]) -> Snapshot:
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

                try:
                    snapshot.average_time = round(float(snapshot.total_time / snapshot.task_count), 2)
                except ZeroDivisionError:
                    snapshot.average_time = 0

        return snapshot

    def build_snapshot_list(self, task_list: list) -> List[Snapshot]:
        snapshot_list = list()
        if len(task_list) > 0:
            snapshot_list = []
            due_date_list = list(set([task.due_date for task in task_list]))
            for index, due_date in enumerate(due_date_list, start=1):
                task_list = self.__tasks.get_tasks_by_date(due_date)
                snapshot = self.build_snapshot(task_list)
                snapshot_list.append(snapshot)

        return snapshot_list

    def update(self, task_list: List[Task]):
        if task_list is not None:
            snapshot_list = self.build_snapshot_list(task_list)
            for snapshot in snapshot_list:
                existing_snapshot = self.__db.get_object("due_date_timestamp", snapshot.due_date_timestamp)
                if existing_snapshot is None:
                    self.__db.append_object(snapshot)
                else:
                    existing_snapshot.update(snapshot)
                    self.__db.replace_object(existing_snapshot)

    def rebuild(self):
        task_list = self.__tasks.get_task_list()
        snapshot_list = self.build_snapshot_list(task_list)
        self.__db.append_objects(snapshot_list)

    def get_all(self, page: int = 0) -> List[Snapshot]:
        self.__db.set_page_number(page)
        return self.__db.get_object_list()

    def get_by_due_date_range(self, min_date: str, max_date: str, page: int = 0) -> List[Snapshot]:
        assert type(min_date) is str
        assert type(max_date) is str

        min_date = self.__date_generator.get_due_date(min_date)
        max_date = self.__date_generator.get_due_date(max_date)
        if min_date is not None and max_date is not None:
            self.__db.set_page_number(page)
            snapshot_list = self.__db.get_filtered_objects("due_date_timestamp",
                                                           min_date.to_timestamp(),
                                                           max_date.to_timestamp())

            return snapshot_list
        else:
            return []

    def get_by_due_date(self, due_date: str) -> List[Snapshot]:
        due_date = self.__date_generator.get_due_date(due_date)
        if due_date is not None:
            snapshot = self.__db.get_object("due_date_timestamp", due_date.to_timestamp())
            if snapshot is not None:
                return [snapshot]
            else:
                return []

    def clear(self):
        self.__db.clear()