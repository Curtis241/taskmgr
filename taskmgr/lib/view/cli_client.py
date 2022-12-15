from datetime import datetime

from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import CsvFileImporter
from taskmgr.lib.view.client import Client
from taskmgr.lib.view.snapshot_list_console_table import SnapshotListConsoleTable
from taskmgr.lib.view.task_console_table import TaskConsoleTable
from taskmgr.lib.view.variable_console_table import VariableConsoleTable


class CliClient(Client):
    """
    Provides cli specific features.
    """
    logger = AppLogger("cli_client").get_logger()

    def __init__(self, db_manager, file_manager):
        super().__init__(db_manager)

        assert isinstance(file_manager, FileManager)
        self.__file_manager = file_manager

        self.task_table = TaskConsoleTable()
        self.snapshot_list_table = SnapshotListConsoleTable()
        self.variables_table = VariableConsoleTable()

    @staticmethod
    def print_message(result: QueryResult):
        page = result.get_page()
        if page.pager_disabled:
            CliClient.logger.info(f"Displaying {result.item_count} row(s)")
        else:
            CliClient.logger.info(f"Displaying {result.item_count} row(s) on page {page.page_number} of {page.page_count}")

    def display_tasks(self, result: QueryResult):
        assert isinstance(result, QueryResult)

        if result.has_data():
            self.print_message(result)

            self.task_table.clear()
            for task in result.to_list():
                self.task_table.add_row(task)

            return self.task_table.print()
        else:
            self.logger.info("No rows to display")

    def display_snapshots(self, result: QueryResult):
        assert isinstance(result, QueryResult)

        if result.has_data():
            self.print_message(result)

            self.snapshot_list_table.clear()
            for snapshot in result.to_list():
                self.snapshot_list_table.add_row(snapshot)

            return self.snapshot_list_table.print()
        else:
            self.logger.info("No rows to display")

    def display_attribute_error(self, param: str, message: str):
        self.logger.info(f"Invalid value. {message}")

    def display_invalid_index_error(self, index: int):
        self.logger.info(f"Provided index {index} is invalid")

    def list_labels(self):
        """
        Lists all labels contained in the tasks
        :return:
        """
        print(f"Labels: {', '.join(self.get_unique_label_list())}")

    def list_projects(self):
        """
        Lists all projects contained in the tasks
        :return:
        """
        print(f"Projects: {', '.join(self.get_unique_project_list())}")

    def list_default_variables(self):
        for key, value in self.get_variables_list():
            self.variables_table.add_row([key, value])
        self.variables_table.print()

    def export_tasks(self, task_list):
        self.__file_manager.save_tasks(task_list)

    def export_snapshots(self, snapshot_list: list):
        self.__file_manager.save_snapshots(snapshot_list)

    def import_tasks(self, csv_file_importer: CsvFileImporter, path: str):
        """
        Imports tasks from the Csv file.
        :param csv_file_importer: CsvFileImporter class
        :param path: path to csv file
        :return: None
        """
        assert isinstance(csv_file_importer, CsvFileImporter)
        assert type(path) is str

        start_datetime = datetime.now()
        self.logger.info(f"Starting import")
        try:
            obj_list = self.__file_manager.open_tasks(path)
            self.logger.info(f"Retrieved {len(obj_list)} tasks from file")
            task_list = csv_file_importer.convert(obj_list)
            self.logger.info(f"Converted rows into task objects")
            sync_results = csv_file_importer.import_tasks(task_list, bulk_save=True)
            self.logger.info(f"Import summary: {sync_results.get_summary()}")
            self.snapshots.rebuild()
            self.logger.info(f"Rebuilding snapshots")

            self.logger.info(f"Import complete: Duration: {self.get_duration(start_datetime)}")
        except Exception as ex:
            self.logger.info(f"ERROR: {ex}")


