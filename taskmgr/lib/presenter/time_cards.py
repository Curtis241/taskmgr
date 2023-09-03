from copy import deepcopy
from datetime import timedelta
from typing import Tuple, Optional, List

from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.database.time_cards_db import TimeCardsDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Calendar
from taskmgr.lib.model.time import Time
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
from taskmgr.lib.variables import CommonVariables


class DueDateError(Exception):
    logger = AppLogger("due_date_error").get_logger()

class TimeCardKeyError(IndexError):
    logger = AppLogger("time_card_key_error").get_logger()
    msg = "timecard.key cannot be found"

    def __init__(self):
        super().__init__(self.msg)
        self.logger.error(self.msg)

class TimeCards:
    """
    Main entry point for querying and managing local time cards.
    """
    logger = AppLogger("time_cards").get_logger()

    def __init__(self, database: TimeCardsDatabase):
        assert isinstance(database, TimeCardsDatabase)

        self.__db = database
        self.__calendar = Calendar()
        self.__vars = CommonVariables()
        self.__date_generator = DateTimeGenerator()

    def get_time_card_by_index(self, index: int) -> TimeCard:
        assert type(index) is int
        return self.__db.get_object("index", index)

    def get_all(self, page: int = 0) -> QueryResult:
        self.__db.set_page_number(page)
        return self.__db.get_all()

    def get_time_card_by_id(self, time_card_id: str) -> TimeCard:
        assert type(time_card_id) is str
        return self.__db.get_object("unique_id", time_card_id)

    def get_time_cards_by_date(self, date_expression: str,
                               add_total: bool = False) -> QueryResult:
        assert type(date_expression) is str
        result = QueryResult()
        days = self.__date_generator.get_days(date_expression)
        for day in days:
            selection = self.__db.get_selected("date_timestamp", day.to_date_timestamp())
            result.extend(selection.to_list())

        if add_total and result.has_data():
            time_card_list = result.to_list()
            time_card = time_card_list[-1]
            time_card.total = self.sum_total_times(time_card_list)

        return result

    def get_time_cards_within_date_range(self, min_date: str, max_date: str, page: int) -> QueryResult:
        assert type(min_date) is str
        assert type(max_date) is str

        min_day = self.__date_generator.get_day(min_date)
        max_day = self.__date_generator.get_day(max_date)

        self.__db.set_page_number(page)
        return self.__db.get_selected("date_timestamp",
                                      min_day.to_date_timestamp(),
                                      max_day.to_date_timestamp())

    def add(self, time_in: str, time_out: str, date_expression: str) -> TimeCard:

        if not date_expression:
            raise DueDateError(f"Provided date {date_expression} is empty")

        if self.__date_generator.validate_input(date_expression,
                                                single_date=True):
            time_card = TimeCard()
            time_in_obj = self.__date_generator.get_time(time_in)
            time_card.time_in = time_in_obj.to_text()

            time_out_obj = self.__date_generator.get_time(time_out)
            time_card.time_out = time_out_obj.to_text()

            date = self.__date_generator.get_day(date_expression)
            time_card.date = date.to_date_string()
            time_card.date_timestamp = date.to_date_timestamp()

            time_card.elapsed_time = self.get_duration(time_in_obj, time_out_obj)

            self.__db.append_object(time_card)
            return time_card

        else:
            raise DueDateError(f"Provided due date {date_expression} is invalid")


    def delete(self, time_card: TimeCard, save: bool = True) -> Optional[TimeCard]:
        """
        Changes the deleted state to True
        :param time_card: TimeCard object
        :param save: Persists the object to redis when True
        :return: Task object
        """
        assert isinstance(time_card, TimeCard)
        if time_card is not None:
            time_card.deleted = True
            if save:
                return self.__db.replace_object(time_card)
            else:
                return time_card
        else:
            raise TimeCardKeyError()


    def undelete(self, time_card: TimeCard) -> Optional[TimeCard]:
        """
        Changes the deleted state to False
        """
        assert isinstance(time_card, TimeCard)
        if time_card is not None:
            time_card.deleted = False
            return self.__db.replace_object(time_card)
        else:
            raise TimeCardKeyError()

    def replace(self, local_time_card: TimeCard, remote_time_card: TimeCard, save: bool = True) -> TimeCard:
        assert isinstance(remote_time_card, TimeCard)
        assert isinstance(local_time_card, TimeCard)

        remote_time_card.index = local_time_card.index
        remote_time_card.unique_id = local_time_card.unique_id
        remote_time_card.date = local_time_card.date
        remote_time_card.date_timestamp = local_time_card.date_timestamp

        if save:
            self.__db.replace_object(remote_time_card, local_time_card.index)
            self.logger.debug(f"Replaced local_time_card: {dict(local_time_card)} with remote_time_card: {dict(remote_time_card)}")
        return remote_time_card

    def insert(self, time_card: TimeCard) -> TimeCard:
        assert isinstance(time_card, TimeCard)
        return self.__db.append_object(time_card)

    def update_all(self, time_card_list: List[TimeCard]) -> List[TimeCard]:
        return self.__db.append_objects(time_card_list)

    def edit(self, index: int,
             time_in: str = None,
             time_out: str = None,
             date_expression: str = None) -> Optional[Tuple[TimeCard, TimeCard]]:
        """
        Modifies a TimeCard object using optional parameters
        """
        original = self.get_time_card_by_index(index)
        if original is not None:
            new_time_card = deepcopy(original)

            if time_in is not None:
                time_in_obj = self.__date_generator.get_time(time_in)
                new_time_card.time_in = time_in_obj.to_text()
            else:
                time_in_obj = self.__date_generator.get_time(original.time_in)

            if time_out is not None:
                time_out_obj = self.__date_generator.get_time(time_out)
                new_time_card.time_out = time_out_obj.to_text()
            else:
                time_out_obj = self.__date_generator.get_time(original.time_out)

            # Duration must be calculated every time function is called. The
            # time must either be pulled from an existing object or provided
            # in the parameters
            new_time_card.elapsed_time = self.get_duration(time_in_obj, time_out_obj)

            if date_expression is not None:
                if self.__date_generator.validate_input(date_expression):
                    day = self.__date_generator.get_day(date_expression)
                    new_time_card.date = day.to_date_string()
                    new_time_card.date_timestamp = day.to_date_timestamp()
                else:
                    self.logger.info(f"Provided due date {date_expression} is invalid")

            return original, self.__db.replace_object(new_time_card)
        else:
            raise TimeCardKeyError()

    def sum_total_times(self, time_cards: List[TimeCard]) -> str:
        """
        Adds list of time in format hh:mm
        """
        time_list = list()
        for time_card in time_cards:
            hours, minutes = str(time_card.elapsed_time).split(":", maxsplit=1)
            time_list.append(timedelta(hours=int(hours), minutes=int(minutes)))

        delta = sum(time_list, start=timedelta())
        return self.to_time_string(delta.seconds)

    @staticmethod
    def to_time_string(total_seconds: int):
        """
        Converts total seconds to hh:ss format
        """
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if hours > 9:
            return f"{int(hours):02}:{int(minutes):02}"
        else:
            return f"{int(hours)}:{int(minutes):02}"

    def get_duration(self, start: Time, end: Time):
        total_seconds = (end.to_datetime() - start.to_datetime()).total_seconds()
        return self.to_time_string(total_seconds)

    def clear(self):
        self.__db.clear()