import textwrap
from datetime import datetime

from beautifultable import BeautifulTable, ALIGN_LEFT, STYLE_BOX
from colored import fg

from taskmgr.lib.date_generator import Calendar, Today, DateGenerator
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables


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

    def __init__(self, tasks):
        assert type(tasks) is Tasks
        self.__tasks = tasks
        self.date_generator = DateGenerator()

    def get_unique_label_list(self):
        return list(self.__tasks.unique(SortType.Label))

    def get_unique_project_list(self):
        return list(self.__tasks.unique(SortType.Project))

    def get_tasks_by_project(self, project):
        assert type(project) is str
        return self.__tasks.get_list_by_type(SortType.Project, project)

    def get_tasks_by_label(self, label):
        assert type(label) is str
        return self.__tasks.get_list_by_type(SortType.Label, label)

    def get_tasks_by_text(self, text):
        assert type(text) is str
        return self.__tasks.get_list_by_type(SortType.Text, text)

    def get_task_list(self):
        return self.__tasks.get_filtered_list()

    def add_task(self, text, label, project, date_expression) -> Task:
        """
        Adds a task
        :param text:
        :param label:
        :param project:
        :param date_expression:
        :return: Task
        """
        assert type(text) is str
        assert type(label) is str
        assert type(project) is str
        assert type(date_expression) is str
        if self.date_generator.validate_input(date_expression):
            task = Task(text)
            task.label = label
            task.project = project
            task.date_expression = date_expression
            self.__tasks.add(task)
            return task
        else:
            self.display_invalid_due_date_error(date_expression)

    def delete_tasks(self, index_tuple) -> list:
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                results.append(self.__tasks.delete(task.id))
            else:
                self.display_invalid_index_error(index)
        return results

    def edit_task(self, index, text, project, label, date_expression) -> Task:
        """
        Edits an existing task by replacing string values. None are allowed
        and handled by the Task object.
        :param index: integer starting at 0
        :param text: name of the task
        :param project:
        :param label:
        :param date_expression:
        :return: Task
        """
        assert type(index) is int
        assert type(date_expression) is str
        task = self.__tasks.get_task_by_index(index)
        if task is None:
            self.display_invalid_index_error(index)

        if self.date_generator.validate_input(date_expression) is False:
            self.display_invalid_due_date_error(date_expression)

        return self.__tasks.edit(task.id, text, label, project, date_expression)

    def complete_tasks(self, index_tuple) -> list:
        """
        Changes the completed status in the DueDate object
        :param index_tuple: int tuple
        :return: list
        """
        assert type(index_tuple) is tuple
        results = list()
        for index in index_tuple:
            task = self.__tasks.get_task_by_index(index)
            if task is not None:
                if task.is_completed() is False:
                    results.append(self.__tasks.complete(task.id))
            else:
                self.display_invalid_index_error(index)
        return results

    def reschedule_tasks(self, today=Today()):
        self.__tasks.reschedule(today)

    def remove_all_tasks(self):
        self.__tasks.clear()

    def display_invalid_index_error(self, index):
        self.logger.info(f"Provided index {index} is invalid")

    def display_invalid_due_date_error(self, date_expression):
        self.logger.info(f"Provided due date {date_expression} is invalid")


class CliClient(Client):
    logger = AppLogger("cli_client").get_logger()

    def __init__(self, tasks, file_exporter):
        super().__init__(tasks)

        self.__file_exporter = file_exporter
        self.__task_list = list()
        self.__calendar = Calendar()
        self.__table = BeautifulTable(default_alignment=ALIGN_LEFT, max_width=200)
        self.__table.set_style(STYLE_BOX)
        self.__table.column_headers = ["#", "Done", "Text", "Project", "Label", "Due Date", "Until"]

        self.__views = [{"action": "group", "sort_type": SortType.Label, "func": self.__group_by_label},
                        {"action": "group", "sort_type": None, "func": self.__display_all_tasks},
                        {"action": "group", "sort_type": SortType.Project, "func": self.__group_by_project},
                        {"action": "filter", "sort_type": SortType.DueDate, "func": self.__filter_by_date},
                        {"action": "filter", "sort_type": SortType.Incomplete,
                         "func": self.__filter_by_incomplete_status},
                        {"action": "filter", "sort_type": SortType.Complete, "func": self.__filter_by_complete_status},
                        {"action": "filter", "sort_type": SortType.Label, "func": self.__filter_by_label},
                        {"action": "filter", "sort_type": SortType.Project, "func": self.__filter_by_project},
                        {"action": "filter", "sort_type": SortType.Text, "func": self.__filter_by_text}]

    @staticmethod
    def format_row(task):
        assert type(task) is Task

        text = textwrap.shorten(task.text, CommonVariables.default_text_field_length, placeholder="...")
        is_completed = task.is_completed()

        if is_completed:
            completed_text = fg('green') + str(is_completed)
        else:
            completed_text = fg('blue') + str(is_completed)

        row = [task.index, completed_text, text, task.project, task.label]
        row.extend(task.get_date_string_list())

        return row

    def get_table(self):
        return self.__table

    def group(self, **kwargs):
        assert "group" in kwargs
        sort_type = kwargs.get("group")

        for view_dict in self.__views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "group":
                func = view_dict["func"]
                return func()

    def filter(self, **kwargs):
        assert "filter" in kwargs
        sort_type = kwargs.get("filter")

        for view_dict in self.__views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "filter":
                func = view_dict["func"]
                kwargs["tasks"] = self.get_task_list()

                # Export table results to markdown file
                table_row_list = func(**kwargs)
                if "export_path" in kwargs and kwargs.get("export_path") is not None:
                    self.__file_exporter.save(table_row_list, kwargs.get("export_path"))
                return table_row_list

    def list_labels(self):
        print("Labels: {}".format(self.get_unique_label_list()))

    def list_projects(self):
        print("Projects: {}".format(self.get_unique_project_list()))

    # Private methods
    def __group_by_label(self):
        self.__clear()
        for label in self.get_unique_label_list():
            for task in self.get_tasks_by_label(label):
                self.__add_table_row(task)
        return self.__print_table()

    def __group_by_project(self):
        self.__clear()
        for project in self.get_unique_project_list():
            for task in self.get_tasks_by_project(project):
                self.__add_table_row(task)
        return self.__print_table()

    def __display_all_tasks(self):
        self.__clear()
        for task in self.get_task_list():
            self.__add_table_row(task)
        return self.__print_table()

    def __clear(self):
        self.__table.clear()
        self.__task_list = list()

    def __print_table(self):
        if len(self.__table) > 0:
            print(self.__table)
            return self.__task_list
        else:
            print("No rows to display. Use add command.")

    def __filter_by_date(self, **kwargs):
        assert "tasks" in kwargs
        self.__clear()
        tasks_list = kwargs.get("tasks")
        filtered_tasks_list = list()
        for task in tasks_list:
            if self.__calendar.contains_today(task.due_dates):
                filtered_tasks_list.append(task)
                self.__add_table_row(task)
        return self.__print_table()

    def __add_table_row(self, task):
        assert type(task) is Task
        row = self.format_row(task)
        self.__table.append_row(row)
        self.__task_list.append(task)

    def __filter_by_incomplete_status(self, **kwargs):
        assert "tasks" in kwargs
        self.__clear()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if not task.is_completed():
                self.__add_table_row(task)
        return self.__print_table()

    def __filter_by_complete_status(self, **kwargs):
        assert "tasks" in kwargs
        self.__clear()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if task.is_completed():
                self.__add_table_row(task)
        return self.__print_table()

    def __filter_by_project(self, **kwargs):
        assert "value" in kwargs
        self.__clear()
        project = kwargs.get("value")
        for task in self.get_tasks_by_project(project):
            self.__add_table_row(task)
        return self.__print_table()

    def __filter_by_label(self, **kwargs):
        assert "value" in kwargs
        self.__clear()
        label = kwargs.get("value")
        for task in self.get_tasks_by_label(label):
            self.__add_table_row(task)
        return self.__print_table()

    def __filter_by_text(self, **kwargs):
        assert "value" in kwargs
        self.__clear()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if str(kwargs.get("value")).lower() in str(task.text).lower():
                self.__add_table_row(task)
        return self.__print_table()
