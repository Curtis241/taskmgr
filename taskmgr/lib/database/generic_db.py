import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, TypeVar, Tuple

from redis import Redis, ResponseError
from redisearch.client import Client
from redisearch.query import Query

from taskmgr.lib.database.pager import Pager, Page
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.variables import CommonVariables

T = TypeVar("T", Snapshot, Task, TimeCard)


class QueryResult:
    def __init__(self, obj_list: list = None, page: Page = None):

        if obj_list is not None:
            self.__object_list = obj_list
            self.item_count = len(self.__object_list)
        else:
            self.__object_list = []
            self.item_count = 0

        if page is not None:
            self.__page = page
        else:
            page = Page()
            page.pager_disabled = True
            self.__page = page

    def get_page(self):
        return self.__page

    def append(self, obj):
        self.__object_list.append(obj)
        self.item_count = len(self.__object_list)

    def extend(self, obj_list: list):
        self.__object_list.extend(obj_list)
        self.item_count = len(self.__object_list)

    def to_list(self):
        return self.__object_list

    def has_data(self) -> bool:
        return self.item_count > 0


class QueryParams:
    def __init__(self, key: str, value1=None, value2=None):
        self.key = key
        self.value1 = value1
        self.value2 = value2

    def build(self) -> Optional[Query]:
        if isinstance(self.value1, str) or isinstance(self.value1, bool):
            return Query(f"@{self.key}:{self.value1}")
        elif isinstance(self.value1, int) and self.value2 is None:
            return Query(f"@{self.key}:[{self.value1} {self.value1}]")
        elif isinstance(self.value1, int) and isinstance(self.value2, int):
            return Query(f"@{self.key}:[{self.value1} {self.value2}]")


class GenericDatabase(ABC):
    """Generic base class to support redis databases."""
    logger = AppLogger("generic_database").get_logger()

    def __init__(self): pass

    @abstractmethod
    def deserialize(self, documents):
        pass

    @abstractmethod
    def create_index(self):
        pass

    @abstractmethod
    def get_key_count(self):
        pass

    @abstractmethod
    def set_page_number(self, page: int): pass

    @staticmethod
    def calc_limits(item_count: int, page_number: int) -> Page:
        row_count = CommonVariables().max_rows
        pager = Pager(item_count, row_count)
        page = pager.get_page(page_number)
        if page is None:
            raise IndexError

        return page

    @abstractmethod
    def replace_object(self, obj: T, index: int = 0) -> T:
        pass

    def _replace_object(self, db: Redis, obj: T, index: int = 0) -> T:

        if self._exists(db):
            with db.pipeline() as pipe:
                if index != 0 and obj.index != index:
                    obj.index = index
                obj.last_updated = self.get_last_updated()

                self.logger.debug(f"replace_object: obj {dict(obj)}")

                for key, value in dict(obj).items():
                    task_key = GenericDatabase.get_key(obj)
                    pipe.hset(task_key, key, value)

                pipe.execute()
            db.save()

            return obj

    @abstractmethod
    def append_object(self, obj: T) -> T:
        pass

    def _append_object(self, db: Redis, obj: T) -> T:
        if self._exists(db):
            with db.pipeline() as pipe:
                obj.index = self.get_key_count() + 1
                obj.unique_id = self.get_unique_id()
                obj.last_updated = self.get_last_updated()

                self.logger.debug(f"append_object: obj {dict(obj)}")

                for key, value in dict(obj).items():
                    obj_key = self.get_key(obj)
                    pipe.hset(obj_key, key, value)

                pipe.execute()
            db.save()

            return obj

    @abstractmethod
    def get_object(self, key: str, value) -> Optional[T]:
        pass

    def _get_object(self, client: Client, key: str, value) -> Optional[T]:

        query = QueryParams(key, value).build()
        if query is None:
            return None

        query.paging(0, 1)
        documents = client.search(query).docs
        obj_list = self.deserialize(documents)
        if obj_list:
            return obj_list[0]
        else:
            return None

    @abstractmethod
    def get_all(self) -> QueryResult:
        pass

    def _get_object_list(self, db: Redis, client: Client, query: Query) -> Tuple[int, List[T]]:
        if self._exists(db):
            try:
                result = client.search(query)
                return int(result.total), self.deserialize(result.docs)
            except ResponseError as ex:
                self.logger.error(ex)

    @abstractmethod
    def append_objects(self, obj_list: List[T]) -> List[T]:
        pass

    def _append_objects(self, db: Redis, obj_list: List[T]) -> List[T]:
        if self._exists(db):
            with db.pipeline() as pipe:
                for obj in obj_list:
                    obj.index = self.get_key_count() + 1
                    obj.unique_id = self.get_unique_id()
                    obj.last_updated = self.get_last_updated()

                    for key, value in dict(obj).items():
                        task_key = self.get_key(obj)
                        pipe.hset(task_key, key, value)

                    pipe.execute()
                db.save()

            return obj_list

    @abstractmethod
    def get_selected(self, key: str, value1, value2=None) -> QueryResult:
        pass

    @abstractmethod
    def clear(self):
        pass

    def _clear(self, db: Redis, pattern: str):
        if self._exists(db):
            for key in db.keys(pattern):
                db.delete(key)
            # db.set(inc_key_name, 0)

    @abstractmethod
    def exists(self) -> bool:
        pass

    @staticmethod
    def _exists(db: Redis) -> bool:
        return db.ping()

    @staticmethod
    def get_key(obj: T):
        return f"{obj.object_name}:{obj.index}"

    @staticmethod
    def get_last_updated() -> str:
        return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_unique_id() -> str:
        return uuid.uuid4().hex
