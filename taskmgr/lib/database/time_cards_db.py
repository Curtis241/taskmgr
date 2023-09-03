from typing import List, Optional

from redis import ResponseError, Redis
from redisearch import IndexDefinition, TextField, NumericField
from redisearch.client import Client
from redisearch.query import Query

from taskmgr.lib.database.generic_db import GenericDatabase, QueryParams, QueryResult
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.time_card import TimeCard


class TimeCardsDatabase(GenericDatabase):

    logger = AppLogger("time_card_database").get_logger()

    def __init__(self, db: Redis):
        super().__init__()
        self.__db = db
        self.__client = Client("timecard:idx", conn=db)
        self.__page_number = 0

    def exists(self) -> bool:
        return self._exists(self.__db)

    def append_object(self, obj: TimeCard) -> TimeCard:
        return self._append_object(self.__db, obj)

    def get_object(self, key: str, value) -> Optional[TimeCard]:
        return self._get_object(self.__client, key, value)

    def append_objects(self, obj_list: List[TimeCard]) -> List[TimeCard]:
        return self._append_objects(self.__db, obj_list)

    def get_selected(self, key: str, value1, value2=None) -> QueryResult:
        query = QueryParams(key, value1, value2).build()
        if query is None:
            return QueryResult()

        try:
            key_count = self.get_key_count()
            page = self.calc_limits(key_count, self.__page_number)
            query.paging(page.offset, page.row_limit)
            query.sort_by("date_timestamp", asc=False)

            total, object_list = self._get_object_list(self.__db, self.__client, query)
            page = self.calc_limits(total, self.__page_number)

            return QueryResult(object_list, page)
        except IndexError:
            return QueryResult()


    def set_page_number(self, page: int):
        self.__page_number = page

    def get_key_count(self) -> int:
        return len(self.__db.keys("TimeCard:*"))

    def replace_object(self, obj: TimeCard, index: int = 0) -> TimeCard:
        return self._replace_object(self.__db, obj, index)

    def get_all(self) -> QueryResult:

        try:
            key_count = self.get_key_count()
            page = self.calc_limits(key_count, self.__page_number)
            query = Query("*").paging(page.offset, page.row_limit).sort_by("date_timestamp", asc=False)
            _, object_list = self._get_object_list(self.__db, self.__client, query)
            return QueryResult(object_list, page)
        except IndexError:
            return QueryResult()

    def deserialize(self, documents) -> List[TimeCard]:
        return [TimeCard().deserialize(document.__dict__) for document in documents]

    def clear(self):
        self._clear(self.__db, "TimeCard:*")

    def create_index(self):
        schema = (
            NumericField("index"),
            TextField("unique_id"),
            TextField("date"),
            NumericField("date_timestamp"),
            TextField("time_in"),
            TextField("time_out"),
            TextField("total"),
        )
        definition = IndexDefinition(prefix=['TimeCard:'])
        try:
            self.__client.info()
        except ResponseError:
            self.__client.create_index(schema, definition=definition)
