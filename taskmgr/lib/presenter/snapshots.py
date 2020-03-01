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
    def count_tasks(project_name: str, tasks_list: list) -> Snapshot:

        snapshot = Snapshot()
        snapshot.project = project_name
        snapshot.timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        for task in tasks_list:
            if task.deleted:
                snapshot.deleted += 1
            elif task.is_completed():
                snapshot.completed += 1
            else:
                snapshot.incomplete += 1
        snapshot.count = len(tasks_list)
        return snapshot
