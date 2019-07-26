from abc import ABC, abstractmethod
from datetime import datetime

from taskmgr.lib.date_generator import Day, DueDate
from taskmgr.lib.google_tasks_api import GTask, GTaskList, TasksListAPI, TasksAPI
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task
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

    def print_summary(self):
        for rule in self.rule_list:
            self.summary_list.append(dict(rule))
        self.logger.debug(f"action: {self.action}, state: {self.state}, result: {self.summary_list}")


class Rule:

    def __init__(self, name, rule_result=False):
        self.name = name
        self.rule_result = rule_result

    def __iter__(self):
        yield "name", self.name
        yield "result", self.rule_result


class SyncAction(ABC):
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


class ExportAction(SyncAction):

    def __init__(self, local_task, remote_task):
        super().__init__(local_task, remote_task)

        assert type(local_task) is GTask
        assert hasattr(local_task, "deleted") is True
        assert hasattr(local_task, "id") is True

        if remote_task is not None:
            assert type(remote_task) is GTask
            assert hasattr(remote_task, "deleted") is True
            assert hasattr(remote_task, "id") is True

    def get_name(self):
        return self.__class__.__name__

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

    def can_delete(self):
        """
        Remote task must exist, and also not be deleted.
        Local task must be deleted
        :return:
        """
        rules = Rules(self.get_name(), "delete")
        rules.add(self.local_task_is_deleted())
        rules.add(self.remote_task_exists())
        rules.add(self.remote_task_is_not_deleted())
        rules.add(self.ids_match())
        rules.print_summary()
        return rules.get_result()

    def can_insert(self):
        """
        Remote task must not exist
        Local task must not be deleted
        :return:
        """
        rules = Rules(self.get_name(), "insert")
        rules.add(self.remote_task_does_not_exist())
        rules.add(self.local_task_is_not_deleted())
        rules.print_summary()
        return rules.get_result()

    def can_update(self):
        """
        Remote task must exist
        Local task must not be deleted
        Local task must not be equal to remote task
        Titles in local and remote task must match
        :return:
        """
        rules = Rules(self.get_name(), "update")
        rules.add(self.remote_task_exists())
        rules.add(self.local_task_is_not_deleted())
        rules.add(self.has_changed())
        rules.add(self.titles_match())
        rules.print_summary()
        return rules.get_result()


class ImportAction(SyncAction):

    def __init__(self, local_task, remote_task):
        super().__init__(local_task, remote_task)

        if local_task is not None:
            assert type(local_task) is Task
            assert hasattr(local_task, "deleted") is True
            assert hasattr(local_task, "external_id") is True
            assert hasattr(local_task, "text") is True

        assert type(remote_task) is Task
        assert hasattr(remote_task, "deleted") is True
        assert hasattr(remote_task, "external_id") is True
        assert hasattr(remote_task, "text") is True

    def get_name(self):
        return self.__class__.__name__

    def external_ids_match(self) -> Rule:
        if self.local_task is not None and self.remote_task is not None:
            return Rule("external_ids_match", self.local_task.external_id == self.remote_task.external_id)
        else:
            return Rule("external_ids_match", False)

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
        rules.add(self.external_ids_match())
        rules.print_summary()
        return rules.get_result()

    def can_update(self):
        """
        Local task must exist
        Remote task must exist
        External ids match
        Remote task is not deleted
        :return:
        """
        rules = Rules(self.get_name(), "update")
        rules.add(self.local_task_exists())
        rules.add(self.remote_task_exists())
        rules.add(self.external_ids_match())
        rules.add(self.remote_task_is_not_deleted())
        rules.print_summary()
        return rules.get_result()

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
        rules.print_summary()
        return rules.get_result()


class Importer:
    logger = AppLogger("importer").get_logger()

    def __init__(self, service, tasks):
        self.tasks = tasks
        self.google_tasks_service = service
        self.tasks_list_api = TasksListAPI(self.google_tasks_service)

    @staticmethod
    def convert_rfc3339_to_date_string(rfc3339_string) -> str:
        dt = datetime.strptime(rfc3339_string, CommonVariables.rfc3339_date_time_format)
        return Day(dt).to_date_string()

    def convert(self) -> list:
        task_list = list()
        for google_taskslist in self.tasks_list_api.list():
            self.logger.info(f"Working on tasks in {google_taskslist.title}")
            for gtask in TasksAPI(google_taskslist.id, self.google_tasks_service).list():

                self.logger.debug(f"Retrieved task {dict(gtask)}")
                if len(gtask.title) != 0:
                    t = Task(gtask.title)
                    t.external_id = gtask.id
                    t.deleted = gtask.deleted
                    t.label = gtask.notes
                    t.project = google_taskslist.title

                    if len(gtask.due) != 0:
                        due_date = DueDate()
                        due_date.completed = bool(gtask.completed)
                        due_date.date_string = self.convert_rfc3339_to_date_string(gtask.due)
                        t.due_dates = [due_date]

                    self.logger.debug(f"Converted task {dict(t)}")
                    task_list.append(t)

        return task_list

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

            item = self.tasks.get_task_by_external_id(remote_task.external_id)
            if item is not None:
                local_task = item.task
            else:
                local_task = None

            action = ImportAction(local_task, remote_task)

            if action.can_delete():
                self.logger.debug(f"Deleting local task {local_task.text}")
                self.tasks.delete(local_task.key)
                sync_results.append(SyncAction.DELETED)

            elif action.can_update():
                self.logger.debug(f"Replacing local task {remote_task.text}")
                self.tasks.replace(remote_task)
                sync_results.append(SyncAction.UPDATED)

            elif action.can_insert():
                self.logger.debug(f"Adding local task {remote_task.text}")
                self.tasks.add(remote_task)
                sync_results.append(SyncAction.ADDED)

            else:
                sync_results.append(SyncAction.SKIPPED)
                self.logger.debug(f"Skipping local task {remote_task.text}")

        return sync_results


class Exporter:
    logger = AppLogger("exporter").get_logger()

    def __init__(self, service, tasks):
        self.google_tasks_service = service
        self.tasks_list_api = TasksListAPI(self.google_tasks_service)
        self.tasks = tasks

    @staticmethod
    def convert_date_string_to_rfc3339(date_string) -> str:
        if len(date_string) > 0:
            dt = datetime.strptime(date_string, CommonVariables.date_format)
            return dt.strftime(CommonVariables.rfc3339_date_time_format)
        return date_string

    def convert(self) -> list:
        """
        Prepares local Task objects for export
        :return:
        """

        gtasks_list = list()
        tasks_list = self.tasks.get_list()
        if len(tasks_list) > 0:

            for project in set([t.project for t in tasks_list]):
                gtasks = GTaskList()
                gtasks.title = project

                for task in tasks_list:
                    if task.project == project:
                        gtask = GTask()
                        gtask.title = task.text
                        gtask.notes = task.label
                        gtask.deleted = task.deleted
                        gtask.id = task.external_id

                        if len(task.due_dates) >= 1:
                            gtask.due = self.convert_date_string_to_rfc3339(task.due_dates[0].date_string)

                        gtask.is_completed(task.is_completed())
                        gtasks.append(gtask)
                gtasks_list.append(gtasks)
        return gtasks_list

    def export_tasks(self, local_task_list) -> SyncResultsList:
        """
        Manages task export to the Google Tasks Service
        :param local_task_list:
        :return:
        """
        self.logger.debug("Starting task export")
        sync_results = SyncResultsList()
        for gtask_list in local_task_list:
            existing_gtask_list = self.tasks_list_api.get(gtask_list.title)
            if existing_gtask_list is None:
                existing_gtask_list = self.tasks_list_api.insert(gtask_list.title)

            tasks_api = TasksAPI(existing_gtask_list.id, self.google_tasks_service)
            for local_gtask in gtask_list.tasks:
                self.logger.debug(f"local task: {dict(local_gtask)}")
                remote_gtask = tasks_api.get(local_gtask.title)

                if remote_gtask is not None:
                    self.logger.debug(f"remote task: {dict(remote_gtask)}")
                else:
                    self.logger.debug(f"remote_task: None")

                action = ExportAction(local_gtask, remote_gtask)
                if action.can_insert():
                    self.logger.debug(f"Inserting task {local_gtask.title} into service")
                    tasks_api.insert(local_gtask)
                    sync_results.append(SyncAction.ADDED)

                elif action.can_update():
                    self.logger.debug(f"Updating task {local_gtask.title} from service")
                    tasks_api.update(local_gtask)
                    sync_results.append(SyncAction.UPDATED)

                elif action.can_delete():
                    self.logger.debug(f"Deleting task {local_gtask.title} from service")
                    tasks_api.delete(local_gtask.title)
                    sync_results.append(SyncAction.DELETED)

                else:
                    self.logger.debug(f"Skipping task {local_gtask.title}")
                    sync_results.append(SyncAction.SKIPPED)

        return sync_results
