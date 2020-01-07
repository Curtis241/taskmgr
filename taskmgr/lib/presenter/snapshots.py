from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.presenter.tasks import Tasks, SortType


class Snapshots(Model):
    logger = AppLogger("snapshots").get_logger()

    def __init__(self, db):
        super().__init__(db, Snapshot())

    def add(self, obj):
        assert type(obj) is Snapshot
        self.append_object(obj)
        self.logger.debug(f"Added {dict(obj)}")
        return obj

    def count_tasks(self, tasks) -> List[Snapshot]:
        assert type(tasks) is Tasks
        for project_name in list(tasks.unique(SortType.Project)):
            tasks_list = tasks.get_list_by_type(SortType.Project, project_name, include_deleted=True)

            summary = Snapshot()
            summary.project = project_name
            for task in tasks_list:
                if task.deleted:
                    summary.deleted += 1
                elif task.is_completed():
                    summary.completed += 1
                else:
                    summary.incomplete += 1
            summary.count = len(tasks_list)
            self.add(summary)

        return self.get_object_list()
