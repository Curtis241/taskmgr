from taskmgr.lib.database.snapshots_db import SnapshotsDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.database.tasks_db import TasksDatabase
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class DatabaseManager:

    def __init__(self, common_vars: CommonVariables = None):
        self.logger = AppLogger("database_manager").get_logger()
        if common_vars is None:
            common_vars = CommonVariables()

        self.__tasks_db = TasksDatabase(common_vars)
        self.__snapshots_db = SnapshotsDatabase(common_vars)

        self.__tasks = Tasks(self.setup_db(self.__tasks_db))
        self.__snapshots = Snapshots(self.__tasks, self.setup_db(self.__snapshots_db))

    def setup_db(self, redis_db):
        if redis_db.exists():
            self.logger.debug("Connecting to redis")
            redis_db.create_index()
            self.logger.debug("Creating index")
            return redis_db
        else:
            self.logger.info("Failed to connect to redis. Check redis host and port")

    def get_tasks_model(self):
        return self.__tasks

    def get_snapshots_model(self):
        return self.__snapshots

    def get_tasks_db(self):
        return self.__tasks_db

    def get_snapshots_db(self):
        return self.__snapshots_db

