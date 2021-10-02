from datetime import datetime

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.snapshot import Snapshot


class Snapshots(Model):
    logger = AppLogger("snapshots").get_logger()

    def __init__(self, db):
        super().__init__(db, Snapshot())

    def add(self, obj):
        assert type(obj) is Snapshot
        self.append_object(obj)
        self.logger.debug(f"Added {dict(obj)}")
        return obj

    def get_snapshot_list(self):
        return self.get_object_list()

    @staticmethod
    def total_count(context: str, project_name: str, task_list: list) -> Snapshot:

        snapshot = Snapshot()
        snapshot.project = project_name
        snapshot.context = context
        snapshot.timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        for task in task_list:
            if task.deleted:
                snapshot.deleted += 1

            if task.is_completed():
                snapshot.completed += 1
            else:
                snapshot.incomplete += 1

        snapshot.count = len(task_list)
        return snapshot



