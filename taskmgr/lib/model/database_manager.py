from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database import RedisDatabase, JsonFileDatabase
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class DatabaseManager:

    def __init__(self, variables=None):
        self.logger = AppLogger("database_manager").get_logger()
        if variables is None:
            self.variables = CommonVariables()
        else:
            self.variables = variables

    def get_database(self):

        if self.variables.enable_redis:
            redis_db = RedisDatabase(self.variables.redis_host, self.variables.redis_port)
            if redis_db.exists():
                self.logger.debug("Connecting to redis")
                return redis_db
            else:
                self.logger.info("Failed to connect to redis. Check redis host and port")
        return JsonFileDatabase()

    def get_tasks_model(self):
        return Tasks(self.get_database())

    def get_snapshots_model(self):
        return Snapshots(self.get_database())
