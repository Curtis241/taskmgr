from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.presenter.tasks import Tasks, SortType


class Snapshots(Model):
    logger = AppLogger("project_summaries").get_logger()

    def __init__(self, file_database):
        super().__init__(file_database)

    def add(self, obj):
        assert type(obj) is Snapshot
        obj.timestamp = self.get_date_time_string()
        obj.index = self.get_index()
        self.append(obj)
        self.logger.debug(f"Added {dict(obj)}")
        self.save()
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

        return self.get_list()

    def from_dict(self, dict_list):
        assert type(dict_list) is list

        for index, obj_dict in enumerate(dict_list):
            obj = Snapshot()
            for key, value in obj_dict.items():
                setattr(obj, key, value)
            self.append(obj)
        return self.get_list()