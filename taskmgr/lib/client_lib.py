from copy import deepcopy
from datetime import datetime

from prettytable import PrettyTable

from taskmgr.lib.date_generator import Calendar, Today, Day, DueDate, DateGenerator
from taskmgr.lib.google_tasks_api import TasksListAPI, TasksAPI, GTask, GTaskList
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables


class ImportResultsList:

    def __init__(self):
        self.__import_results = list()
        self.__added_count = 0
        self.__deleted_count = 0
        self.__updated_count = 0
        self.__skipped_count = 0

    def get_list(self):
        return self.__import_results

    def append(self, import_object):
        assert type(import_object) is ImportObject

        if import_object.action == ImportObject.ADDED:
            self.__added_count += 1
        if import_object.action == ImportObject.DELETED:
            self.__deleted_count += 1
        if import_object.action == ImportObject.UPDATED:
            self.__updated_count += 1
        if import_object.action == ImportObject.SKIPPED:
            self.__skipped_count += 1

        self.__import_results.append(import_object)

    def get_summary(self):
        return f"added: {self.__added_count}, deleted: {self.__deleted_count}, updated: {self.__updated_count}, " \
            f"skipped: {self.__skipped_count} "


class ImportObject:
    SKIPPED = 'skipped'
    UPDATED = 'updated'
    DELETED = 'deleted'
    ADDED = 'added'

    def __init__(self, task, action):
        self.__task = task
        self.__action = action

    @property
    def action(self):
        return self.__action

    @property
    def task(self):
        return self.__task

    def __iter__(self):
        yield "action", self.__action
        yield "task", dict(self.__task)


class SyncClient(object):
    logger = AppLogger("sync_client").get_logger()

    def __init__(self, service, tasks):

        self.tasks = tasks
        self.google_tasks_service = service
        self.tasks_list_api = TasksListAPI(self.google_tasks_service)

    @staticmethod
    def convert_date_string_to_rfc3339(date_string) -> str:
        dt = datetime.strptime(date_string, CommonVariables.date_format)
        return dt.strftime(CommonVariables.rfc3339_date_time_format)

    @staticmethod
    def convert_rfc3339_to_date_string(rfc3339_string) -> str:
        dt = datetime.strptime(rfc3339_string, CommonVariables.rfc3339_date_time_format)
        return Day(dt).to_date_string()

    def pull_tasks_from_service(self) -> list:
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

    def push_tasks_to_service(self, gtask_lists):

        for gtask_list in gtask_lists:
            if len(gtask_list.title) > 0:
                existing_gtask_list = self.tasks_list_api.get(gtask_list.title)
                if existing_gtask_list is None:
                    existing_gtask_list = self.tasks_list_api.insert(gtask_list.title)

                tasks_api = TasksAPI(existing_gtask_list.id, self.google_tasks_service)
                for gtask in gtask_list.tasks:
                    existing_gtask = tasks_api.get(gtask.title)
                    if existing_gtask is None:
                        tasks_api.insert(gtask)
                    else:
                        if existing_gtask.deleted:
                            tasks_api.delete(existing_gtask.title)
                        else:
                            tasks_api.update(gtask)

            else:
                self.logger.debug("Cannot insert tasklist because title is null")

    def export_tasks(self, tasks_list) -> list:
        assert type(tasks_list) is list

        gtasks_list = list()
        if len(tasks_list) > 0:

            for project in set([t.project for t in tasks_list]):
                gtasks = GTaskList()
                gtasks.title = project

                for task in tasks_list:
                    if task.project == project:
                        gtask = GTask()
                        gtask.title = task.text
                        gtask.notes = task.label
                        gtask.id = task.external_id

                        if len(task.due_dates) >= 1:
                            gtask.due = self.convert_date_string_to_rfc3339(task.due_dates[0].date_string)

                        gtask.is_completed(task.is_completed())
                        gtasks.append(gtask)
                gtasks_list.append(gtasks)
        return gtasks_list

    def import_tasks(self, task_list) -> ImportResultsList:
        assert type(task_list) is list
        import_results = ImportResultsList()
        for task in task_list:
            assert type(task) is Task

            item = self.tasks.get_task_by_external_id(task.external_id)
            if item is not None:
                self.logger.debug(f"Found task {item.task.text} in db")
                if task.deleted:
                    deleted_task = deepcopy(self.tasks.delete(item.task.key))
                    import_results.append(ImportObject(deleted_task, ImportObject.DELETED))

                else:
                    task = deepcopy(self.tasks.replace(task))
                    import_results.append(ImportObject(task, ImportObject.UPDATED))

            else:
                if not task.deleted:
                    self.logger.debug(f"Selected task {task.text} does not exist in db")
                    added_task = self.tasks.add(task)
                    import_results.append(ImportObject(added_task, ImportObject.ADDED))
                else:
                    import_results.append(ImportObject(task, ImportObject.SKIPPED))
                    self.logger.debug(f"Skipping task {task.text} because it is already deleted")

        return import_results

    def sync(self):
        start_datetime = datetime.now()
        self.logger.info(f"Starting import")
        import_task_list = self.pull_tasks_from_service()
        self.logger.info(f"Retrieved {len(import_task_list)} tasks from service")
        import_results = self.import_tasks(import_task_list)
        self.logger.info(f"Import summary: {import_results.get_summary()}")
        self.logger.info(f"Import complete")

        self.logger.info(f"Starting export")
        export_task_list = self.tasks.get_list()
        self.logger.info(f"Preparing {len(export_task_list)} tasks for export")
        gtasks_list = self.export_tasks(export_task_list)
        if gtasks_list is not None:
            self.logger.info(f"Exporting tasks to service")
            self.push_tasks_to_service(gtasks_list)

        end_datetime = datetime.now()
        duration = (end_datetime - start_datetime).total_seconds()
        self.logger.info(f"Export complete: (Duration: {duration})")


class Client:
    logger = AppLogger("client").get_logger()

    def __init__(self):
        self.tasks = Tasks()
        self.date_generator = DateGenerator()

    def add_task(self, text, label, project, date_expression):

        if self.date_generator.validate_input(date_expression):
            task = Task(text)
            task.label = label
            task.project = project
            task.date_expression = date_expression
            self.tasks.add(task)
            return task
        else:
            self.display_invalid_due_date_error(date_expression)
            return None

    def get_filtered_list(self):
        return [task for task in self.tasks.get_list() if not task.deleted]

    def delete_task(self, keys):
        assert type(keys) is tuple
        for key in keys:
            if self.tasks.get_task_by_key(key) is not None:
                self.tasks.delete(key)
            else:
                self.display_invalid_key_error(key)

    def edit_task(self, **kwargs):
        key = kwargs.get("key")
        date_expression = kwargs.get("due_date")

        if self.tasks.get_task_by_key(key) is None:
            self.display_invalid_key_error(key)
            return None

        if self.date_generator.validate_input(date_expression):
            self.display_invalid_due_date_error(date_expression)
            return None

        return self.tasks.edit(key, kwargs.get("text"), kwargs.get("label"), kwargs.get("project"),
                               date_expression)

    def complete_task(self, **kwargs):
        key = kwargs.get("key")
        if self.tasks.get_task_by_key(key) is None:
            self.display_invalid_key_error(key)
            return None

        self.tasks.complete(key)

    def reschedule_tasks(self, today=Today()):
        self.tasks.reschedule(today)

    def remove_all_tasks(self):
        self.tasks.clear()

    def display_invalid_key_error(self, key):
        self.logger.info(f"Provided key {key} is invalid")

    def display_invalid_due_date_error(self, date_expression):
        self.logger.info(f"Provided due date {date_expression} is invalid")


class CliClient(Client):
    logger = AppLogger("cli_client").get_logger()

    def __init__(self):
        super().__init__()
        self.calendar = Calendar()
        self.rows = list()

        self.table = PrettyTable(["Id", "Done", "Text", "Project", "Label", "Due Date", "Until"])
        self.table.align["Id"] = "l"
        self.table.align["Done"] = "l"
        self.table.align["Text"] = "l"
        self.table.align["Project"] = "l"
        self.table.align["Label"] = "l"
        self.table.align["Due Date"] = "l"
        self.table.align["Until"] = "l"

        self.views = [{"action": "group", "sort_type": SortType.Label, "func": self.__group_by_label},
                      {"action": "group", "sort_type": None, "func": self.__display_all_tasks},
                      {"action": "group", "sort_type": SortType.Project, "func": self.__group_by_project},
                      {"action": "filter", "sort_type": SortType.DueDate, "func": self.__filter_by_date},
                      {"action": "filter", "sort_type": SortType.Incomplete,
                       "func": self.__filter_by_incomplete_status},
                      {"action": "filter", "sort_type": SortType.Complete, "func": self.__filter_by_complete_status},
                      {"action": "filter", "sort_type": SortType.Label, "func": self.__filter_by_label},
                      {"action": "filter", "sort_type": SortType.Project, "func": self.__filter_by_project}]

    def __add_row(self, task):
        self.rows.append(task)
        row_list = task.get_task_status()
        self.table.add_row(row_list)

    def __print_table(self):
        if len(self.rows) > 0:
            print(self.table.get_string())
            return self.rows
        else:
            print("No rows to display. Use add command.")

    def group_tasks(self, sort_type=None):
        self.rows = list()
        for view_dict in self.views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "group":
                func = view_dict["func"]
                return func()

    def filter_tasks(self, **kwargs):
        self.rows = list()
        sort_type = kwargs.get("filter")
        for view_dict in self.views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "filter":
                func = view_dict["func"]
                kwargs["tasks"] = self.get_filtered_list()
                return func(**kwargs)

    def __list_labels(self):
        print("Labels: {}".format(list(self.tasks.unique(SortType.Label))))

    def __list_projects(self):
        print("Projects: {}".format(list(self.tasks.unique(SortType.Project))))

    def __group_by_label(self):
        self.table.clear_rows()
        for label in self.tasks.unique(SortType.Label):
            for task in self.tasks.get_list_by_type(SortType.Label, label):
                self.__add_row(task)
        return self.__print_table()

    def __group_by_project(self):
        self.table.clear_rows()
        for project in self.tasks.unique(SortType.Project):
            for task in self.tasks.get_list_by_type(SortType.Project, project):
                self.__add_row(task)
        return self.__print_table()

    def __display_all_tasks(self):
        self.table.clear_rows()
        for task in self.get_filtered_list():
            self.__add_row(task)
        return self.__print_table()

    def __filter_by_date(self, **kwargs):
        self.table.clear_rows()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if self.calendar.contains_today(task.due_dates):
                self.__add_row(task)
        return self.__print_table()

    def __filter_by_incomplete_status(self, **kwargs):
        self.table.clear_rows()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if not task.is_completed():
                self.__add_row(task)
        return self.__print_table()

    def __filter_by_complete_status(self, **kwargs):
        self.table.clear_rows()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if task.is_completed():
                self.__add_row(task)
        return self.__print_table()

    def __filter_by_project(self, **kwargs):
        print(f"filter_by_project: {kwargs}")

    def __filter_by_label(self, **kwargs):
        print(f"filter_by_label {kwargs}")
