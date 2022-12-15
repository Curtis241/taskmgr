from typing import List, Optional

from redis import ResponseError, Redis
from redisearch import IndexDefinition, TextField, NumericField
from redisearch.client import Client
from redisearch.query import Query

from taskmgr.lib.database.generic_db import GenericDatabase, QueryParams, QueryResult
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot


class SnapshotsDatabase(GenericDatabase):

    logger = AppLogger("snapshot_database").get_logger()

    def __init__(self, db: Redis):
        super().__init__()
        self.__db = db
        self.__client = Client("snapshot:idx", conn=db)
        self.__page_number = 0

    def exists(self) -> bool:
        return self._exists(self.__db)

    def append_object(self, obj: Snapshot) -> Snapshot:
        return self._append_object(self.__db, obj)

    def get_object(self, key: str, value) -> Optional[Snapshot]:
        return self._get_object(self.__client, key, value)

    def append_objects(self, obj_list: List[Snapshot]) -> List[Snapshot]:
        return self._append_objects(self.__db, obj_list)

    def get_selected(self, key: str, value1, value2=None) -> QueryResult:
        query = QueryParams(key, value1, value2).build()
        if query is None:
            return QueryResult()

        try:
            key_count = self.get_key_count()
            page = self.calc_limits(key_count, self.__page_number)
            query.paging(page.offset, page.row_limit)
            query.sort_by("due_date_timestamp", asc=False)

            total, object_list = self._get_object_list(self.__db, self.__client, query)
            page = self.calc_limits(total, self.__page_number)

            return QueryResult(object_list, page)
        except IndexError:
            return QueryResult()


    def set_page_number(self, page: int):
        self.__page_number = page

    def get_key_count(self) -> int:
        return len(self.__db.keys("Snapshot:*"))

    def replace_object(self, obj: Snapshot, index: int = 0) -> Snapshot:
        return self._replace_object(self.__db, obj, index)

    def get_all(self) -> QueryResult:

        try:
            key_count = self.get_key_count()
            page = self.calc_limits(key_count, self.__page_number)
            query = Query("*").paging(page.offset, page.row_limit).sort_by("due_date_timestamp", asc=False)
            _, object_list = self._get_object_list(self.__db, self.__client, query)
            return QueryResult(object_list, page)
        except IndexError:
            return QueryResult()

    def deserialize(self, documents) -> List[Snapshot]:
        return [Snapshot().deserialize(document.__dict__) for document in documents]

    def clear(self):
        self._clear(self.__db, "Snapshot:*")

    def create_index(self):
        schema = (
            NumericField("index"),
            TextField("unique_id"),
            TextField("due_date"),
            NumericField("due_date_timestamp"),
            NumericField("count"),
            NumericField("completed"),
            NumericField("incomplete"),
            NumericField("deleted"),
            NumericField("average_time"),
            NumericField("total_time")

        )
        definition = IndexDefinition(prefix=['Snapshot:'])
        try:
            self.__client.info()
        except ResponseError:
            self.__client.create_index(schema, definition=definition)
