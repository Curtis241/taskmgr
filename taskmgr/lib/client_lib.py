from datetime import datetime

from prettytable import PrettyTable

from taskmgr.lib.date_generator import Calendar, Today, DateGenerator
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import SortType, Tasks


class SyncClient(object):
    logger = AppLogger("sync_client").get_logger()

    def __init__(self, importer, exporter):
        self.importer = importer
        self.exporter = exporter

    @staticmethod
    def get_duration(start_datetime):
        end_datetime = datetime.now()
        total_seconds = (end_datetime - start_datetime).total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}m:{:02}s'.format(int(minutes), int(seconds))

    def sync(self, export_enabled=False, import_enabled=False):
        start_datetime = datetime.now()

        if import_enabled:
            self.logger.info(f"Starting import")
            import_task_list = self.importer.convert()
            self.logger.info(f"Retrieved {len(import_task_list)} tasks from service")
            sync_results = self.importer.import_tasks(import_task_list)
            self.logger.info(f"Import summary: {sync_results.get_summary()}")

            self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")

        if export_enabled:
            self.logger.info(f"Starting export")
            self.logger.info(f"Preparing tasks for export")
            gtasks_list = self.exporter.convert()
            self.logger.info(f"Exporting tasks to service")
            sync_results = self.exporter.export_tasks(gtasks_list)
            self.logger.info(f"Export summary: {sync_results.get_summary()}")

            self.logger.info(f"Export complete: Duration: {self.get_duration(start_datetime)}")


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
                return self.tasks.delete(key)
            else:
                self.display_invalid_key_error(key)

    def edit_task(self, **kwargs):
        key = kwargs.get("key")
        date_expression = kwargs.get("due_date")

        if self.tasks.get_task_by_key(key) is None:
            self.display_invalid_key_error(key)
            return None

        if self.date_generator.validate_input(date_expression) is False:
            self.display_invalid_due_date_error(date_expression)
            return None

        return self.tasks.edit(key, kwargs.get("text"), kwargs.get("label"), kwargs.get("project"),
                               date_expression)

    def complete_task(self, keys):
        assert type(keys) is tuple
        for key in keys:
            if self.tasks.get_task_by_key(key) is not None:
                return self.tasks.complete(key)
            else:
                self.display_invalid_key_error(key)

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
