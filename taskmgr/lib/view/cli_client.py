from taskmgr.lib.logger import AppLogger
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
        self.task_table = TaskConsoleTable()
        self.snapshots_table = SnapshotConsoleTable()
        self.variables_table = VariableConsoleTable()

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
        for key, value in self.get_variables_list():
            self.variables_table.add_row([key, value])
        self.variables_table.print()

    def __print_tasks_table(self, task_list, show_deleted=False):
        self.task_table.clear()
        if show_deleted:
            for task in task_list:
                self.task_table.add_row(task)
        else:
            for task in task_list:
                if task.deleted is False:
                    self.task_table.add_row(task)
        return self.task_table.print()

    def __print_snapshots_table(self, snapshot_list):
        self.snapshots_table.clear()
        for snapshot in snapshot_list:
            self.snapshots_table.add_row(snapshot)
        return self.snapshots_table.print()

    def __export_tasks(self, task_list, **kwargs):
        if "export" in kwargs:
            file_type = kwargs.get("export")
            self.__file_exporter.save_tasks(task_list, file_type)

    def group_by_label(self, **kwargs):
        """
        Displays all tasks and sorts by label
        :return: task_list
        """
        task_list = list()
        for label in self.get_unique_label_list():
            for task in self.get_tasks_by_label(label):
                task_list.append(task)

        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def group_by_project(self, **kwargs):
        """
        Displays all tasks and sorts by project
        :return: task_list
        """
        task_list = list()
        for project in self.get_unique_project_list():
            for task in self.get_tasks_by_project(project):
                task_list.append(task)

        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def display_all_tasks(self, **kwargs):
        """
        Simple list of all tasks without any sorting applied.
        :return: task_list
        """
        task_list = self.get_task_list()
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list, kwargs.get("all"))

    def filter_by_today(self, **kwargs):
        """
        Filters the tasks that contain today's date.
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        task_list = self.get_tasks_for_today()
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_due_date(self, **kwargs):
        """
        Filters the tasks that contain today's date.
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "date" in kwargs

        date_string = kwargs.get("date")
        task_list = self.get_tasks_by_date(date_string)
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_due_date_range(self, **kwargs):
        """
        Filters the tasks that are between the min date and the max date
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "min_date" in kwargs
        assert "max_date" in kwargs

        min_date_string = kwargs.get("min_date")
        max_date_string = kwargs.get("max_date")

        task_list = self.get_tasks_within_date_range(min_date_string, max_date_string)
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_status(self, **kwargs):
        """
        Filters tasks by the status either complete or incomplete
        :param kwargs: kwargs[tasks] contains tasks_list
        :return: task_list
        """
        assert "status" in kwargs

        status_type = kwargs.get("status")
        if status_type == "incomplete":
            task_list = self.get_tasks_by_status(is_completed=False)
        else:
            task_list = self.get_tasks_by_status(is_completed=True)

        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_project(self, **kwargs):
        """
        Filters tasks by project
        :param kwargs: kwargs[value] contains a project_name
        :return: task_list
        """
        assert "project" in kwargs

        project = kwargs.get("project")
        task_list = self.get_tasks_by_project(project)
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_label(self, **kwargs):
        """
        Filters tasks by label
        :param kwargs: kwargs[value] contains a label
        :return: task_list
        """
        assert "label" in kwargs

        label = kwargs.get("label")
        task_list = self.get_tasks_by_label(label)
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def filter_by_text(self, **kwargs):
        """
        Filters tasks by text. Similar to a text search
        :param kwargs: kwargs[value] contains the title of a task and depends on kwargs[tasks]
        :return: task_list
        """
        assert "text" in kwargs

        text = str(kwargs.get("text"))
        task_list = self.get_tasks_by_text(text)
        self.__export_tasks(task_list, **kwargs)
        return self.__print_tasks_table(task_list)

    def count_all_tasks(self, **kwargs):

        tasks_list = self.get_task_list()
        snapshot_list = self.count_tasks(tasks_list)
        self.save_snapshots(snapshot_list)

        if kwargs.get("export") is not None:
            self.__file_exporter.save_snapshots(self.get_snapshot_list())

        if kwargs.get("silent") is False:
            tasks_list = self.__print_snapshots_table(snapshot_list)

        return tasks_list

    def count_by_due_date_range(self, **kwargs):
        assert "min_date" in kwargs
        assert "max_date" in kwargs

        min_date_string = kwargs.get("min_date")
        max_date_string = kwargs.get("max_date")

        task_list = self.get_tasks_within_date_range(min_date_string, max_date_string)
        snapshot_list = self.count_tasks(task_list)

        return self.__print_snapshots_table(snapshot_list)

    def count_by_due_date(self, **kwargs):
        assert "date" in kwargs

        date_string = kwargs.get("date")
        task_list = self.get_tasks_by_date(date_string)
        snapshot_list = self.count_tasks(task_list)

        return self.__print_snapshots_table(snapshot_list)

    def count_by_today(self):
        task_list = self.get_tasks_for_today()
        snapshot_list = self.count_tasks(task_list)

        return self.__print_snapshots_table(snapshot_list)

    def count_by_project(self, **kwargs):
        assert "project" in kwargs

        project = kwargs.get("project")
        task_list = self.get_tasks_by_project(project)
        snapshot_list = self.count_tasks(task_list)

        return self.__print_snapshots_table(snapshot_list)

    def count_by_status(self, **kwargs):
        assert "status" in kwargs

        status_type = kwargs.get("status")
        if status_type == "complete":
            task_list = self.get_tasks_by_status(is_completed=True)
        else:
            task_list = self.get_tasks_by_status(is_completed=False)

        snapshot_list = self.count_tasks(task_list)
        return self.__print_snapshots_table(snapshot_list)

    def count_by_label(self, **kwargs):
        assert "label" in kwargs

        label = kwargs.get("label")
        task_list = self.get_tasks_by_label(label)
        snapshot_list = self.count_tasks(task_list)
        return self.__print_snapshots_table(snapshot_list)




