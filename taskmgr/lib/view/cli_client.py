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

    def __init__(self, db_manager, file_manager):
        super().__init__(db_manager, file_manager)

        self.task_table = TaskConsoleTable()
        self.snapshots_table = SnapshotConsoleTable()
        self.variables_table = VariableConsoleTable()

    def display_tasks(self, task_list, kwargs):
        task_list = self.__print_tasks_table(task_list, kwargs.get("all"))
        self.__export_tasks(task_list, **kwargs)
        return task_list

    def display_snapshots(self, snapshot_list, kwargs):
        self.save_snapshots(snapshot_list)
        if kwargs.get("export") is not None:
            self.save_snapshots_to_file(snapshot_list)

        self.__print_snapshots_table(snapshot_list)
        return snapshot_list

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
        if "export" in kwargs and kwargs.get("export") is True:
            self.save_tasks_to_file(task_list)
