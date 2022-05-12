from typing import List

import redis
from redis import ResponseError
from redisearch import IndexDefinition, TextField, NumericField, Client

from taskmgr.lib.database.generic import GenericDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task


class TasksDatabase(GenericDatabase):
    """
    Manages saving and retrieving objects to a redis database. Retrieve method should be called
    before save to maintain a consistent state.
    """
    logger = AppLogger("task_database").get_logger()

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.db = redis.Redis(host=self.host, port=self.port, db=0)
        self.client = Client("idx:task")

    @staticmethod
    def __key(task: Task):
        assert isinstance(task, Task), "Expecting type Task"
        return f"{task.object_name}:{task.index}"

    def replace_object(self, task: Task, index: int = 0) -> Task:
        """
        Replaces an object in Redis database using Task.index value in object
        OR uses index when it is provided.
        :param task: Task object
        :param index: External Task object index
        :return: Task object
        """
        assert isinstance(task, Task), "Expecting type Task"

        if self.exists():
            with self.db.pipeline() as pipe:
                if index != 0:
                    task.index = index
                task.last_updated = self.get_last_updated()

                self.logger.debug(f"replace_object: task {dict(task)}")

                for key, value in dict(task).items():
                    task_key = self.__key(task)
                    pipe.hset(task_key, key, value)

                pipe.execute()
            self.db.save()

            return task

    def update_objects(self, task_list: List[Task]) -> List[Task]:

        if self.exists():
            with self.db.pipeline() as pipe:
                for task in task_list:
                    task.index = self.db.incrby("task_incr")
                    task.unique_id = self.get_unique_id()
                    task.last_updated = self.get_last_updated()

                    for key, value in dict(task).items():
                        task_key = self.__key(task)
                        pipe.hset(task_key, key, value)

                    pipe.execute()
            self.db.bgsave()

            return task_list

    def append_object(self, task: Task) -> Task:
        """
        Updates or inserts new objects that inherit from DatabaseObject.
        When key matches existing key an update occurs, but if there
        is no match then a new key is created.
        :param task: Class object
        :return: None
        """
        assert isinstance(task, Task), "Expecting type Task"

        if self.exists():
            with self.db.pipeline() as pipe:
                task.index = self.db.incrby("task_incr")
                task.unique_id = self.get_unique_id()
                task.last_updated = self.get_last_updated()

                self.logger.debug(f"append_object: task {dict(task)}")

                for key, value in dict(task).items():
                    task_key = self.__key(task)
                    pipe.hset(task_key, key, value)

                pipe.execute()
            self.db.save()

            return task

    def get_object_list(self) -> List[Task]:
        return [Task().deserialize(self.db.hgetall(key)) for key in sorted(self.db.keys("Task:*"))]

    def exists(self):
        return self.db.ping()

    def clear(self):
        self.db.flushdb()

    def create_index(self):
        schema = (
            TextField("index"),
            TextField("text"),
            TextField("label"),
            TextField("deleted"),
            TextField("project"),
            TextField("completed"),
            TextField("unique_id"),
            NumericField("due_date")
        )
        definition = IndexDefinition(prefix=['Task:'])
        try:
            self.client.info()
        except ResponseError:
            self.client.create_index(schema, definition=definition)