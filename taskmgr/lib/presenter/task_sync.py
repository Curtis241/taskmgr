import ast
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from taskmgr.lib.presenter.date_generator import Day
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task
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
    def decompose(task):
        if task is not None:
            return dict(task)
        return 'None'

    def print_summary(self, local_task, remote_task, rule_result):
        for rule in self.rule_list:
            self.summary_list.append(dict(rule))

        self.logger.debug(f"action: {self.action}, state: {self.state}, rule_result: {rule_result}, "
                          f"summary: {self.summary_list}, local_task: "
                          f"{self.decompose(local_task)}, remote_task: {self.decompose(remote_task)}")


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

    def __init__(self, local_task, remote_task):
        self.__local_task = local_task
        self.__remote_task = remote_task

    @property
    def local_task(self):
        return self.__local_task

    @local_task.setter
    def local_task(self, local_task):
        self.__local_task = local_task

    @property
    def remote_task(self):
        return self.__remote_task

    @remote_task.setter
    def remote_task(self, remote_task):
        self.__remote_task = remote_task

    def remote_task_exists(self) -> Rule:
        return Rule("remote_task_exists", self.remote_task is not None)

    def remote_task_does_not_exist(self) -> Rule:
        return Rule("remote_task_does_not_exist", self.remote_task is None)

    def remote_task_is_deleted(self) -> Rule:
        if self.remote_task is not None:
            return Rule("remote_task_is_deleted", self.remote_task.deleted is True)
        else:
            return Rule("remote_task_is_deleted", False)

    def local_task_exists(self) -> Rule:
        return Rule("local_task_exists", self.local_task is not None)

    def local_task_does_not_exist(self) -> Rule:
        return Rule("local_task_does_not_exist", self.local_task is None)

    def remote_task_is_not_deleted(self) -> Rule:
        if self.remote_task is not None:
            return Rule("remote_task_is_not_deleted", self.remote_task.deleted is False)
        else:
            return Rule("remote_task_is_not_deleted", False)

    def local_task_is_deleted(self) -> Rule:
        if self.local_task is not None:
            return Rule("local_task_is_deleted", self.local_task.deleted is True)
        else:
            return Rule("local_task_is_deleted", False)

    def local_task_is_not_deleted(self) -> Rule:
        if self.local_task is not None:
            return Rule("local_task_is_not_deleted", self.local_task.deleted is False)
        else:
            return Rule("local_task_is_not_deleted", False)

    def has_changed(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("has_changed", dict(self.local_task) != dict(self.remote_task))
        else:
            return Rule("has_changed", False)

    def ids_match(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("external_ids_match", self.local_task.id == self.remote_task.id)
        else:
            return Rule("external_ids_match", False)

    def titles_match(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("titles_match", self.local_task.title == self.remote_task.title)
        else:
            return Rule("titles_match", False)

    def external_ids_match(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("external_ids_match", self.local_task.external_id == self.remote_task.external_id)
        else:
            return Rule("external_ids_match", False)

    def names_match(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("names_match", self.local_task.text == self.remote_task.text)
        else:
            return Rule("names_match", False)

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


class ImportAction(SyncAction):
    """
    Defines the delete, insert, and update rules for importing tasks.
    """

    def __init__(self, local_task, remote_task):
        super().__init__(local_task, remote_task)

        if local_task is not None:
            assert type(local_task) is Task
            assert hasattr(local_task, "deleted") is True
            assert hasattr(local_task, "text") is True

        assert type(remote_task) is Task
        assert hasattr(remote_task, "deleted") is True
        assert hasattr(remote_task, "text") is True

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
        rules.add(self.remote_task_is_deleted())
        rules.add(self.local_task_exists())
        rules.add(self.local_task_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
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
        rules.add(self.local_task_exists())
        rules.add(self.remote_task_exists())
        rules.add(self.remote_task_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
        return rule_result

    def can_insert(self):
        """
        Local task must not exist
        Remote task must exist
        Remote task must not be deleted
        :return:
        """
        rules = Rules(self.get_name(), "insert")
        rules.add(self.local_task_does_not_exist())
        rules.add(self.remote_task_exists())
        rules.add(self.remote_task_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
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


class Importer:
    logger = AppLogger("importer").get_logger()

    def __init__(self, tasks):
        self.__tasks = tasks

    @abstractmethod
    def get_tasks_by_id(self, remote_task):
        pass

    def import_tasks(self, remote_task_list) -> SyncResultsList:
        """
        Manage task import from Google Tasks Service
        :param remote_task_list:
        :return ImportResultsList:
        """
        assert type(remote_task_list) is list
        sync_results = SyncResultsList()
        for remote_task in remote_task_list:
            assert type(remote_task) is Task

            local_task = self.get_tasks_by_id(remote_task)
            action = ImportAction(local_task, remote_task)

            if action.can_delete():
                self.__tasks.delete(local_task.unique_id)
                sync_results.append(SyncAction.DELETED)

            elif action.can_update():
                self.__tasks.replace(local_task, remote_task)
                sync_results.append(SyncAction.UPDATED)

            elif action.can_insert():
                self.__tasks.append(remote_task)
                sync_results.append(SyncAction.ADDED)

            else:
                sync_results.append(SyncAction.SKIPPED)
                self.logger.debug(f"Skipping local task {remote_task.text}")

        return sync_results


class CsvFileImporter(Importer):
    logger = AppLogger("csv_file_importer").get_logger()

    def __init__(self, tasks):
        super().__init__(tasks)
        self.__tasks = tasks

    def get_tasks_by_id(self, remote_task):
        return self.__tasks.get_task_by_id(remote_task.unique_id)

    @staticmethod
    def convert(obj_list: list) -> List[Task]:
        task_list = list()
        for obj_dict in obj_list:
            task = Task(obj_dict["text"])
            for key, value in obj_dict.items():
                if key == "deleted":
                    value = ast.literal_eval(value)
                    task.deleted = value
                elif key == "due_date":
                    task.due_date.date_string = value
                elif key == "done":
                    value = ast.literal_eval(value)
                    task.due_date.completed = value
                else:
                    setattr(task, key, value)
            task_list.append(task)
        return task_list

