from taskmgr.lib.logger import AppLogger
from taskmgr.lib.presenter.date_generator import Calendar, Today
from taskmgr.lib.presenter.tasks import SortType
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.client import Client
from taskmgr.lib.view.snapshot_console_table import SnapshotConsoleTable
from taskmgr.lib.view.task_console_table import TaskConsoleTable
from taskmgr.lib.view.variable_console_table import VariableConsoleTable


class CliClient(Client):
    """
    Provides cli specific features.
    """
    logger = AppLogger("cli_client").get_logger()

    def __init__(self, db_manager, file_exporter):
        super().__init__(db_manager)

        self.__file_exporter = file_exporter

        # Task list is needed to store the tasks to allow
        # unit tests to check the output
        self.__task_list = list()
        self.__calendar = Calendar()
        self.task_table = TaskConsoleTable()
        self.snapshots_table = SnapshotConsoleTable()
        self.variables_table = VariableConsoleTable()

        # Maps the available group and filter options to the appropriate methods. This makes it easy to
        # add filter or group methods that only do one thing only. Using the single responsibility principle
        # in this way makes the code more maintainable.
        self.__views = [{"action": "group", "sort_type": SortType.Label, "func": self.__group_by_label},
                        {"action": "group", "sort_type": None, "func": self.__display_all_tasks},
                        {"action": "group", "sort_type": SortType.Project, "func": self.__group_by_project},
                        {"action": "filter", "sort_type": SortType.DueDate, "func": self.__filter_by_due_date},
                        {"action": "filter", "sort_type": SortType.Today, "func": self.__filter_by_today},
                        {"action": "filter", "sort_type": SortType.DueDateRange,
                         "func": self.__filter_by_due_date_range},
                        {"action": "filter", "sort_type": SortType.Status, "func": self.__filter_by_status},
                        {"action": "filter", "sort_type": SortType.Label, "func": self.__filter_by_label},
                        {"action": "filter", "sort_type": SortType.Project, "func": self.__filter_by_project},
                        {"action": "filter", "sort_type": SortType.Text, "func": self.__filter_by_text}]

    def count(self):
        for snapshot in self.count_tasks():
            self.snapshots_table.add_row(snapshot)
        return self.snapshots_table.print()

    def group(self, **kwargs):
        """
        Main method that groups the tasks by sorting. Depends on receiving
        kwargs parameters from cli.py.
        :param kwargs: kwargs[group] must be one of label, project, or None
        :return: task list
        """
        assert "group" in kwargs
        sort_type = kwargs.get("group")

        for view_dict in self.__views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "group":
                func = view_dict["func"]
                return func()

    def filter(self, **kwargs):
        """
        Main method that filters the tasks. Depends on receiving kwargs parameters from cli.py.
        Also allows results to be saved to a markdown file, if the export_path parameter
        is provided.
        :param kwargs: kwargs[filter] must be one of due_date, incomplete, complete, text, label, and project
        :return: task_list
        """
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
        """
        Lists all labels contained in the tasks
        :return:
        """
        print("Labels: {}".format(self.get_unique_label_list()))

    def list_projects(self):
        """
        Lists all projects contained in the tasks
        :return:
        """
        print("Projects: {}".format(self.get_unique_project_list()))

    def set_default_variables(self, **kwargs):
        self.set_defaults(kwargs)

    def list_default_variables(self):
        for key, value in dict(CommonVariables()).items():
            self.variables_table.add_row([key, value])
        self.variables_table.print()

    # Private methods
    def __group_by_label(self):
        """
        Displays all tasks and sorts by label
        :return: task_list
        """
        self.task_table.clear()
        for label in self.get_unique_label_list():
            for task in self.get_tasks_by_label(label):
                self.task_table.add_row(task)
        return self.task_table.print()

    def __group_by_project(self):
        """
        Displays all tasks and sorts by project
        :return: task_list
        """
        self.task_table.clear()
        for project in self.get_unique_project_list():
            for task in self.get_tasks_by_project(project):
                self.task_table.add_row(task)
        return self.task_table.print()

    def __display_all_tasks(self):
        """
        Simple list of all tasks without any sorting applied.
        :return: task_list
        """
        self.task_table.clear()
        for task in self.get_task_list():
            self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_today(self, **kwargs):
        """
        Filters the tasks that contain today's date.
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "tasks" in kwargs
        self.task_table.clear()
        tasks_list = kwargs.get("tasks")

        filtered_tasks_list = list()
        for task in tasks_list:
            if self.__calendar.contains_due_date(task.due_dates, date_string=Today().to_date_string()):
                filtered_tasks_list.append(task)
                self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_due_date(self, **kwargs):
        """
        Filters the tasks that contain today's date.
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "tasks" in kwargs
        self.task_table.clear()
        tasks_list = kwargs.get("tasks")
        date_string = kwargs.get("date")

        filtered_tasks_list = list()
        for task in tasks_list:
            if self.__calendar.contains_due_date(task.due_dates, date_string=date_string):
                filtered_tasks_list.append(task)
                self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_due_date_range(self, **kwargs):
        """
        Filters the tasks that are between the min date and the max date
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "tasks" in kwargs
        self.task_table.clear()
        tasks_list = kwargs.get("tasks")
        filtered_tasks_list = list()
        min_date_string = kwargs.get("min_date")
        max_date_string = kwargs.get("max_date")
        for task in tasks_list:
            if self.__calendar.contains_due_date_range(min_date_string, max_date_string, task.due_dates):
                filtered_tasks_list.append(task)
                self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_status(self, **kwargs):
        """
        Filters tasks by the status either complete or incomplete
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "tasks" in kwargs
        self.task_table.clear()
        tasks_list = kwargs.get("tasks")
        status_type = kwargs.get("value")

        if status_type == "incomplete":

            for task in tasks_list:
                if not task.is_completed():
                    self.task_table.add_row(task)
            return self.task_table.print()

        elif status_type == "complete":

            for task in tasks_list:
                if task.is_completed():
                    self.task_table.add_row(task)
            return self.task_table.print()

        return self.task_table.print()

    def __filter_by_project(self, **kwargs):
        """
        Filters tasks by project
        :param kwargs: kwargs[value] contains a project_name
        :return: task_list
        """
        assert "value" in kwargs
        self.task_table.clear()
        project = kwargs.get("value")
        for task in self.get_tasks_by_project(project):
            self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_label(self, **kwargs):
        """
        Filters tasks by label
        :param kwargs: kwargs[value] contains a label
        :return: task_list
        """
        assert "value" in kwargs
        self.task_table.clear()
        label = kwargs.get("value")
        for task in self.get_tasks_by_label(label):
            self.task_table.add_row(task)
        return self.task_table.print()

    def __filter_by_text(self, **kwargs):
        """
        Filters tasks by text. Similar to a text search
        :param kwargs: kwargs[value] contains the title of a task and depends on kwargs[tasks]
        :return: task_list
        """
        assert "value" in kwargs
        self.task_table.clear()
        tasks_list = kwargs.get("tasks")
        for task in tasks_list:
            if str(kwargs.get("value")).lower() in str(task.text).lower():
                self.task_table.add_row(task)
        return self.task_table.print()
