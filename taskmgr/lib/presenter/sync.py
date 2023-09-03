from abc import ABC, abstractmethod
from datetime import datetime

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.day import Day
from taskmgr.lib.variables import CommonVariables


class SyncResultsList:

    def __init__(self):
        self.__sync_results = list()
        self.__added_count = 0
        self.__deleted_count = 0
        self.__updated_count = 0
        self.__skipped_count = 0

    def get_list(self):
        return self.__sync_results

    def append(self, sync_action):
        # assert type(sync_action) is SyncAction

        if sync_action == SyncAction.ADDED:
            self.__added_count += 1
        if sync_action == SyncAction.DELETED:
            self.__deleted_count += 1
        if sync_action == SyncAction.UPDATED:
            self.__updated_count += 1
        if sync_action == SyncAction.SKIPPED:
            self.__skipped_count += 1

        self.__sync_results.append(sync_action)

    def get_summary(self):
        return f"added: {self.__added_count}, deleted: {self.__deleted_count}, updated: {self.__updated_count}, " \
               f"skipped: {self.__skipped_count} "


class Rules:
    """
    Aggregates rule objects and retrieves the result from multiple rules. It also provides an effective way
    to debug the result of import and export rules.
    """
    logger = AppLogger("rules").get_logger()

    def __init__(self, action, state):
        self.action = action
        self.state = state
        self.rule_list = list()
        self.summary_list = list()

    def add(self, rule):
        assert type(rule) is Rule
        self.rule_list.append(rule)

    def get_result(self):
        for rule in self.rule_list:
            if rule.rule_result is False:
                return False
        return True

    @staticmethod
    def decompose(obj):
        if obj is not None:
            return dict(obj)
        return 'None'

    def print_summary(self, local_obj, remote_obj, rule_result):
        for rule in self.rule_list:
            self.summary_list.append(dict(rule))

        self.logger.debug(f"action: {self.action}, state: {self.state}, rule_result: {rule_result}, "
                          f"summary: {self.summary_list}, local_obj: "
                          f"{self.decompose(local_obj)}, remote_obj: {self.decompose(remote_obj)}")


class Rule:

    def __init__(self, name, rule_result=False):
        self.name = name
        self.rule_result = rule_result

    def __iter__(self):
        yield "name", self.name
        yield "result", self.rule_result


class SyncAction(ABC):
    """
    Generic base class for the ImportAction class. The methods that are common are placed
    in this class to avoid duplication. The public properties below act as a simple enum, instead of passing
    strings the public property is used instead.
    """
    SKIPPED = 'skipped'
    UPDATED = 'updated'
    DELETED = 'deleted'
    ADDED = 'added'

    def __init__(self, local_obj, remote_obj):
        self.__local_obj = local_obj
        self.__remote_obj = remote_obj

        if self.__local_obj is not None:
            assert hasattr(self.__local_obj, "deleted") is True

        assert hasattr(self.__remote_obj, "deleted") is True

    @property
    def local_obj(self):
        return self.__local_obj

    @local_obj.setter
    def local_obj(self, local_obj):
        self.__local_obj = local_obj

    @property
    def remote_obj(self):
        return self.__remote_obj

    @remote_obj.setter
    def remote_obj(self, remote_obj):
        self.__remote_obj = remote_obj

    def remote_obj_exists(self) -> Rule:
        return Rule("remote_obj_exists", self.remote_obj is not None)

    def remote_obj_is_deleted(self) -> Rule:
        if self.remote_obj is not None:
            return Rule("remote_obj_is_deleted", self.remote_obj.deleted is True)
        else:
            return Rule("remote_obj_is_deleted", False)

    def local_obj_exists(self) -> Rule:
        return Rule("local_obj_exists", self.local_obj is not None)

    def local_obj_does_not_exist(self) -> Rule:
        return Rule("local_obj_does_not_exist", self.local_obj is None)

    def remote_obj_is_not_deleted(self) -> Rule:
        if self.remote_obj is not None:
            return Rule("remote_obj_is_not_deleted", self.remote_obj.deleted is False)
        else:
            return Rule("remote_obj_is_not_deleted", False)

    def local_obj_is_not_deleted(self) -> Rule:
        if self.local_obj is not None:
            return Rule("local_obj_is_not_deleted", self.local_obj.deleted is False)
        else:
            return Rule("local_obj_is_not_deleted", False)

    @abstractmethod
    def can_delete(self):
        pass

    @abstractmethod
    def can_update(self):
        pass

    @abstractmethod
    def can_insert(self):
        pass

    @abstractmethod
    def get_name(self):
        pass


class ImportActions(SyncAction):
    """
    Defines the delete, insert, and update rules for importing tasks.
    """

    def __init__(self, local_object, remote_object):
        super().__init__(local_object, remote_object)

    def get_name(self):
        return self.__class__.__name__

    def can_delete(self):
        """
        Remote task must be deleted
        Local task must exist
        Local task must not be deleted
        External id in local and remote tasks must match
        :return:
        """
        rules = Rules(self.get_name(), "delete")
        rules.add(self.remote_obj_is_deleted())
        rules.add(self.local_obj_exists())
        rules.add(self.local_obj_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_obj, self.remote_obj, rule_result)
        return rule_result

    def can_update(self):
        """
        Local task must exist
        Remote task must exist
        Names match
        Remote task is not deleted
        :return:
        """
        rules = Rules(self.get_name(), "update")
        rules.add(self.local_obj_exists())
        rules.add(self.remote_obj_exists())
        rules.add(self.remote_obj_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_obj, self.remote_obj, rule_result)
        return rule_result

    def can_insert(self):
        """
        Local task must not exist
        Remote task must exist
        Remote task must not be deleted
        :return:
        """
        rules = Rules(self.get_name(), "insert")
        rules.add(self.local_obj_does_not_exist())
        rules.add(self.remote_obj_exists())
        rules.add(self.remote_obj_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_obj, self.remote_obj, rule_result)
        return rule_result


class Converter:
    logger = AppLogger("converter").get_logger()

    @staticmethod
    def rfc3339_to_date_string(rfc3339_string) -> str:
        dt = datetime.strptime(rfc3339_string, CommonVariables().rfc3339_date_time_format)
        return Day(dt).to_date_string()

    @staticmethod
    def date_string_to_rfc3339(date_string) -> str:
        variables = CommonVariables()
        if len(date_string) > 0:
            dt = datetime.strptime(date_string, variables.date_format)
            return dt.strftime(variables.rfc3339_date_time_format)
        return date_string
