from taskmgr.lib.logger import AppLogger
from taskmgr.lib.database.tasks_db import TasksDatabase
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class DatabaseManager:

    def __init__(self, common_variables: CommonVariables = None):
        self.logger = AppLogger("database_manager").get_logger()
        if common_variables is not None:
            self.variables = common_variables
        else:
            self.variables = CommonVariables()

        self.__database = TasksDatabase(self.variables.redis_host, self.variables.redis_port)
        self.__tasks = Tasks(self.get_database(self.__database))

    def get_database(self, redis_db):
        if redis_db.exists():
            self.logger.debug("Connecting to redis")
            redis_db.create_index()
            self.logger.debug("Creating index")
            return redis_db
        else:
            self.logger.info("Failed to connect to redis. Check redis host and port")

    def get_tasks_model(self):
        return self.__tasks

    def get_tasks_db(self):
        return self.__database

