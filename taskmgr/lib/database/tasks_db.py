from typing import List, Optional

from redis import ResponseError
from redisearch import IndexDefinition, TextField, NumericField, reducers
from redisearch.aggregation import AggregateRequest
from redisearch.query import Query

from taskmgr.lib.database.generic_db import GenericDatabase, QueryParams
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task
from taskmgr.lib.variables import CommonVariables


class TasksDatabase(GenericDatabase):
    """
    Manages saving and retrieving objects to a redis database. Retrieve method should be called
    before save to maintain a consistent state.
    """
    logger = AppLogger("task_database").get_logger()

    def __init__(self, common_vars: CommonVariables):
        super().__init__("tasks_inc_key")
        self.__db, self.__client = self._build(common_vars, "task:idx")
        self.__page_number = 0

    def set_page_number(self, page: int):
        self.__page_number = page

    def exists(self) -> bool:
        return self._exists(self.__db)

    def append_object(self, obj: Task) -> Task:
        return self._append_object(self.__db, obj)

    def get_object(self, key: str, value) -> Optional[Task]:
        return self._get_object(self.__client, key, value)

    def append_objects(self, obj_list: List[Task]) -> List[Task]:
        return self._append_objects(self.__db, obj_list)

    def get_filtered_objects(self, key: str, value1, value2=None) -> List[Task]:
        query = QueryParams(key, value1, value2).build()
        if query is None:
            return []
        try:
            key_count = self.get_key_count()
            offset, max_limit = self.calc_limits(key_count, self.__page_number)
            query.paging(offset, max_limit)
            query.sort_by("due_date_timestamp", asc=False)
            return self._get_object_list(self.__db, self.__client, query)
        except IndexError:
            return []

    def get_key_count(self) -> int:
        return len(self.__db.keys("Task:*"))

    def replace_object(self, obj: Task, index: int = 0) -> Task:
        return self._replace_object(self.__db, obj, index)

    def get_object_list(self) -> List[Task]:
        try:
            key_count = self.get_key_count()
            offset, max_limit = self.calc_limits(key_count, self.__page_number)
            query = Query("*").paging(offset, max_limit).sort_by("due_date_timestamp", asc=False)
            return self._get_object_list(self.__db, self.__client, query)
        except IndexError:
            return []

    def unique(self, key: str) -> List[str]:
        if self.exists():
            try:
                request = AggregateRequest('*')
                request.group_by(f"@{key}", reducers.count())
                aggregate_result = self.__client.aggregate(request)
                if aggregate_result.rows:
                    return [str(row[1], 'utf-8') for row in aggregate_result.rows]
            except ResponseError as ex:
                self.logger.error(ex)

    def deserialize(self, documents) -> List[Task]:
        return [Task().deserialize(document.__dict__) for document in documents]

    def clear(self):
        self._clear(self.__db, "Task:*")

    def create_index(self):
        schema = (
            NumericField("index"),
            TextField("name"),
            TextField("label"),
            TextField("deleted"),
            TextField("project"),
            TextField("completed"),
            TextField("unique_id"),
            TextField("due_date"),
            NumericField("due_date_timestamp")
        )
        definition = IndexDefinition(prefix=['Task:'])
        try:
            self.__client.info()
        except ResponseError:
            self.__client.create_index(schema, definition=definition)
