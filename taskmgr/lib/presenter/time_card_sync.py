import uuid
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
from taskmgr.lib.presenter.sync import ImportActions, SyncResultsList, SyncAction


class TimeCardImporter:
    logger = AppLogger("importer").get_logger()

    def __init__(self, time_cards):
        self.__time_cards = time_cards
        self.__date_generator = DateTimeGenerator()

    def convert(self, obj_list: list) -> List[TimeCard]:
        time_card_list = list()

        for obj_dict in obj_list:

            added_time_in = None
            added_time_out = None
            time_card = TimeCard()

            for key, value in obj_dict.items():
                if key == "deleted":
                    value = True if str(value).lower() == "true" else False
                    time_card.deleted = value

                elif key == "time_in":
                    added_time_in = value

                elif key == "time_out":
                    added_time_out = value

                elif key == "date":
                    day = self.__date_generator.get_day(value)
                    time_card.date = day.to_date_string()
                    time_card.date_timestamp = day.to_date_timestamp()

                else:
                    setattr(time_card, key, value)

            if time_card.unique_id is None:
                time_card.unique_id = uuid.uuid4().hex

            if added_time_in is not None and added_time_out is not None:
                time_in_obj = self.__date_generator.get_time(added_time_in)
                time_out_obj = self.__date_generator.get_time(added_time_out)

                time_card.time_in = time_in_obj.to_text()
                time_card.time_out = time_out_obj.to_text()

                time_card.elapsed_time = self.__time_cards.get_duration(time_in_obj, time_out_obj)

            time_card_list.append(time_card)
            
        return time_card_list

    def import_objects(self, remote_obj_list) -> SyncResultsList:
        """
        Manage time card import from csv file
        :param remote_obj_list: TimeCards contained in file
        :return SyncResultsList:
        """
        assert type(remote_obj_list) is list
        sync_results = SyncResultsList()
        object_list = list()

        for remote_object in remote_obj_list:
            assert type(remote_object) is TimeCard

            local_object = self.__time_cards.get_time_card_by_id(remote_object.unique_id)
            action = ImportActions(local_object, remote_object)

            if action.can_delete():
                self.logger.debug("deleting time card")
                object_list.append(self.__time_cards.delete(local_object))
                sync_results.append(SyncAction.DELETED)

            elif action.can_update():
                self.logger.debug("updating time card")
                object_list.append(self.__time_cards.replace(local_object, remote_object))
                sync_results.append(SyncAction.UPDATED)

            elif action.can_insert():
                self.logger.debug("inserting time card")
                object_list.append(self.__time_cards.insert(remote_object))
                sync_results.append(SyncAction.ADDED)

            else:
                sync_results.append(SyncAction.SKIPPED)
                self.logger.debug(f"Skipping local time card {remote_object.name}")

        return sync_results



