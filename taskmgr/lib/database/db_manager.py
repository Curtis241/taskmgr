from redis import Redis

from taskmgr.lib.database.snapshots_db import SnapshotsDatabase
from taskmgr.lib.database.tasks_db import TasksDatabase
from taskmgr.lib.database.time_cards_db import TimeCardsDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.presenter.time_cards import TimeCards
from taskmgr.lib.variables import CommonVariables

class AuthenticationFailed(Exception):
    logger = AppLogger("authentication_failed").get_logger()
    def __init__(self, msg):
        super().__init__(msg)
        self.logger.error(msg)
        self.logger.info(msg)

class DatabaseManager:

    def __init__(self, common_vars: CommonVariables = None):
        self.logger = AppLogger("database_manager").get_logger()
        if common_vars is None:
            common_vars = CommonVariables()

        host = common_vars.redis_host
        port = common_vars.redis_port
        if host not in ["localhost", "127.0.0.1"]:
            username = common_vars.redis_username
            password = common_vars.redis_password
            if username != "unset" and password != "unset":
                self.__connection = Redis(host=host, port=port, db=0,
                                          username=username,
                                          password=password)
            else:
                raise AuthenticationFailed("Failed to connect to redis. Check redis credentials in variables.ini")
        else:
            self.__connection = Redis(host=host, port=port, db=0)

    def initialize(self, redis_db):
        if redis_db.exists():
            self.logger.debug("Connecting to redis")
            redis_db.create_index()
            self.logger.debug("Creating index")
            return redis_db
        else:
            self.logger.info("Failed to connect to redis. Check redis host and port")

    def get_tasks_model(self):
        tasks_db = self.get_tasks_db()
        return Tasks(tasks_db)

    def get_snapshots_model(self):
        tasks = self.get_tasks_model()
        time_cards = self.get_time_cards_model()
        snapshot_db = self.get_snapshots_db()
        return Snapshots(tasks, time_cards, snapshot_db)

    def get_time_cards_model(self):
        time_cards_db = self.get_time_cards_db()
        return TimeCards(time_cards_db)

    def get_tasks_db(self):
        tasks_db = TasksDatabase(self.__connection)
        return self.initialize(tasks_db)

    def get_snapshots_db(self):
        snapshots_db = SnapshotsDatabase(self.__connection)
        return self.initialize(snapshots_db)

    def get_time_cards_db(self):
        time_cards_db = TimeCardsDatabase(self.__connection)
        return self.initialize(time_cards_db)


