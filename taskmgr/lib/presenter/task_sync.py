from abc import ABC, abstractmethod
from datetime import datetime

from taskmgr.lib.model.gtask_project import GTaskProject
from taskmgr.lib.presenter.date_generator import Day, DueDate
from taskmgr.lib.presenter.gtask_project_api import GTasksProjectAPI
from taskmgr.lib.presenter.gtasks_api import GTask, GTasksAPI
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
    Generic base class for the ImportAction and ExportAction classes. The methods that are common are placed
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


class ExportAction(SyncAction):
    """
    Defines the delete, insert, and update rules for exporting tasks. I removed the complex if..then logic in the
    exporter and replaced it with methods that encapsulate the operation specific rules.
    """

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

    def can_delete(self):
        """
        Rules:
        Titles must match
        Remote task must exist, and also not be deleted.
        Local task must be deleted
        :return: rule_result
        """
        rules = Rules(self.get_name(), "delete")
        rules.add(self.local_task_is_deleted())
        rules.add(self.remote_task_exists())
        rules.add(self.remote_task_is_not_deleted())
        rules.add(self.titles_match())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
        return rule_result

    def can_insert(self):
        """
        Rules:

        Remote task must not exist
        Local task must not be deleted
        :return: rule_result
        """
        rules = Rules(self.get_name(), "insert")
        rules.add(self.remote_task_does_not_exist())
        rules.add(self.local_task_is_not_deleted())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
        return rule_result

    def can_update(self):
        """
        Rules:

        Remote task must exist
        Local task must not be deleted
        Local task must not be equal to remote task
        Titles in local and remote task must match
        :return: rule_result
        """
        rules = Rules(self.get_name(), "update")
        rules.add(self.remote_task_exists())
        rules.add(self.local_task_is_not_deleted())
        rules.add(self.has_changed())
        rules.add(self.ids_match())
        rule_result = rules.get_result()
        rules.print_summary(self.local_task, self.remote_task, rule_result)
        return rule_result


class ImportAction(SyncAction):
    """
    Defines the delete, insert, and update rules for importing tasks.
    """

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
        rules.add(self.external_ids_match())
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

    @staticmethod
    def to_gtask_project(tasks_list: list, project_name: str) -> GTaskProject:
        assert type(tasks_list) is list
        assert type(project_name) is str

        gtask_project = GTaskProject()
        gtask_project.title = project_name
        Converter.logger.info(f"Working on tasks in {project_name}")

        for task in tasks_list:
            if task.project == gtask_project.title:
                gtask = GTask()
                gtask.title = task.text
                gtask.notes = task.label
                gtask.deleted = task.deleted
                gtask.id = task.external_id
                gtask.due = Converter.date_string_to_rfc3339(task.due_date.date_string)
                gtask.is_completed(task.is_completed())
                gtask.source_task = task
                gtask_project.append(gtask)

        return gtask_project

    @staticmethod
    def to_task(gtask: GTask, project_name: str) -> Task:
        assert isinstance(gtask, GTask)
        assert type(project_name) is str

        Converter.logger.debug(f"{gtask.title}")

        task = Task(gtask.title)
        task.external_id = gtask.id
        task.deleted = gtask.deleted
        task.label = gtask.notes
        task.project = project_name

        due_date = DueDate()
        if len(gtask.due) != 0:
            due_date.completed = bool(gtask.is_completed)
            due_date.date_string = Converter.rfc3339_to_date_string(gtask.due)

        elif len(gtask.completed) != 0:
            due_date.completed = bool(gtask.is_completed)
            due_date.date_string = Converter.rfc3339_to_date_string(gtask.completed)

        else:
            due_date.completed = False
            due_date.date_string = str()
        task.due_date = due_date

        return task


class GoogleTasksImporter:
    logger = AppLogger("google_tasks_importer").get_logger()

    def __init__(self, google_tasks_service, tasks):
        self.__tasks = tasks
        self.__google_tasks_service = google_tasks_service
        self.__gtasks_project_api = GTasksProjectAPI(self.__google_tasks_service)
        self.__converter = Converter

    def get_projects(self):
        return self.__gtasks_project_api.list()

    def convert_local_tasks(self, project_name) -> list:
        """
        Converts local tasks to Google Tasks List
        :param project_name:
        :return:
        """
        assert type(project_name) is str

        task_list = list()
        project = self.__gtasks_project_api.get(project_name)
        self.logger.info(f"Working on tasks in {project.title}")
        for gtask in GTasksAPI(project.id, self.__google_tasks_service).list():
            if len(gtask.title) != 0:
                task_list.append(self.__converter.to_task(gtask, project.title))

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

            local_task = self.__tasks.get_task_by_external_id(remote_task.external_id)
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


class GoogleTasksExporter:
    logger = AppLogger("google_tasks_exporter").get_logger()

    def __init__(self, google_tasks_service, tasks):
        self.__google_tasks_service = google_tasks_service
        self.__gtasks_project_api = GTasksProjectAPI(google_tasks_service)
        self.__tasks = tasks
        self.__converter = Converter

    def get_projects(self):
        return set([t.project for t in self.__tasks.get_object_list()])

    def convert_local_tasks(self, project_name) -> list:
        """
        Prepares local Task objects for export
        :type project_name: string
        :return:
        """
        assert type(project_name) is str

        project_list = list()
        tasks_list = self.__tasks.get_object_list()
        if len(tasks_list) > 0:
            project_list.append(self.__converter.to_gtask_project(tasks_list, project_name))

        return project_list

    def export_tasks(self, local_project_list) -> SyncResultsList:
        """
        Manages task export to the Google Tasks Service
        :param local_project_list: list of GTaskProject objects
        :return: SyncResultsList object
        """
        self.logger.debug("Starting task export")
        sync_results = SyncResultsList()
        for local_project in local_project_list:
            remote_project = self.__gtasks_project_api.get(local_project.title)
            if remote_project is None:
                # If the project does not exist then create one.
                remote_project = self.__gtasks_project_api.insert(local_project.title)

            api = GTasksAPI(remote_project.id, self.__google_tasks_service)
            for local_gtask in local_project.tasks:

                if len(local_gtask.id) > 0:
                    # If the task has been imported previously it will have an gtask.id, but
                    # if it has been created locally then it will not.
                    remote_gtask = api.get_by_id(local_gtask.id)
                else:
                    # Select using the title if the id does not exist.
                    remote_gtask = api.get_by_title(local_gtask.title)

                action = ExportAction(local_gtask, remote_gtask)
                if action.can_insert():
                    remote_gtask = api.insert(local_gtask)
                    sync_results.append(SyncAction.ADDED)

                    remote_task = Converter.to_task(remote_gtask, local_project.title)
                    local_task = local_gtask.source_task
                    # After it is inserted then the local object needs to be updated to
                    # preserve the gtask.id so it can be updated in the google tasks service.
                    self.__tasks.replace(local_task, remote_task)

                elif action.can_update():
                    api.update(local_gtask)
                    sync_results.append(SyncAction.UPDATED)

                elif action.can_delete():
                    api.delete(local_gtask.title)
                    sync_results.append(SyncAction.DELETED)

                else:
                    self.logger.debug(f"Skipping task {local_gtask.title}")
                    sync_results.append(SyncAction.SKIPPED)

        return sync_results
