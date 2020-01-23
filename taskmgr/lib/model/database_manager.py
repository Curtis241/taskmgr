from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database import RedisDatabase, JsonFileDatabase
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class DatabaseManager:

    logger = AppLogger("database_manager").get_logger()

    @staticmethod
    def get_database():
        variables = CommonVariables()
        if variables.enable_redis:
            redis_db = RedisDatabase(variables.redis_host, variables.redis_port)
            if redis_db.exists():
                DatabaseManager.logger.debug("Connecting to redis")
                return redis_db
            else:
                DatabaseManager.logger.info("Failed to connect to redis. Check redis host and port")
        return JsonFileDatabase()

    def get_tasks_model(self):
        return Tasks(self.get_database())

    def get_snapshots_model(self):
        return Snapshots(self.get_database())