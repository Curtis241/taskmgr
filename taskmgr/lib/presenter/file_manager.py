import csv
import os
import time
from abc import abstractmethod
from operator import attrgetter

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.variables import CommonVariables


class UnexpectedColumnCount(Exception): pass


class File:
    logger = AppLogger("file").get_logger()

    def __init__(self):
        self.__output_dir = CommonVariables().resources_dir

    @staticmethod
    def get_timestamp():
        return time.strftime(CommonVariables().file_name_timestamp)

    def open(self, path):
        if os.path.exists(path):
            self.logger.info(f"Reading file {path}")
            return self.read_file(path)
        else:
            raise FileNotFoundError(f"Path {path} does not exist")

    def save(self, obj_list) -> str:
        if obj_list is not None:
            assert type(obj_list) is list

            file_name = self.get_filename()
            path = self.__make_path(self.__output_dir, file_name)

            if os.path.exists(self.__output_dir):
                self.write_file(path, obj_list)
                self.logger.info(f"Saved results to {path}")
                return path
            else:
                raise FileNotFoundError(f"Path {path} does not exist")

    @staticmethod
    def __make_path(file_path, file_name) -> str:
        if str(file_path).endswith("/"):
            path = f"{file_path}{file_name}"
        else:
            path = f"{file_path}/{file_name}"
        return path

    @abstractmethod
    def write_file(self, path, task_list):
        pass

    @abstractmethod
    def read_file(self, path):
        pass

    @abstractmethod
    def get_filename(self):
        pass


class CsvTasksFile(File):

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"tasks_{self.get_timestamp()}.csv"

    def write_file(self, path, task_list):
        with open(path, 'w', newline='') as csvfile:
            if len(task_list) > 0:
                writer = csv.DictWriter(csvfile, fieldnames=self.__get_field_names())
                writer.writeheader()
                for task in sorted(task_list, key=attrgetter('index')):
                    writer.writerow(self.__write_row(task))

    def read_file(self, path):
        obj_list = list()
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            expected_column_count = len(CsvTasksFile.__get_field_names())
            for row in reader:
                if len(row.keys()) == expected_column_count:
                    obj_list.append(row)
                else:
                    raise UnexpectedColumnCount(f"Expected {expected_column_count} columns in csv file")
        return obj_list

    @staticmethod
    def __get_field_names():
        return ["index", "done", "text", "project", "label", "due_date",
                "last_updated", "deleted", "unique_id"]

    @staticmethod
    def __write_row(task):
        return {"index": task.index,
                "done": task.is_completed(),
                "text": task.text,
                "project": task.project,
                "label": task.label,
                "due_date": task.due_date.date_string,
                "last_updated": task.last_updated,
                "deleted": task.deleted,
                "unique_id": task.unique_id}


class CsvSnapshotsFile(File):

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"snapshots_{self.get_timestamp()}.csv"

    def write_file(self, path, snapshot_list):
        with open(path, 'w', newline='') as csvfile:
            if len(snapshot_list) > 0:
                writer = csv.DictWriter(csvfile, fieldnames=self.__get_field_names())
                writer.writeheader()
                for snapshot in sorted(snapshot_list, key=attrgetter('index')):
                    writer.writerow(self.__write_row(snapshot))

    def read_file(self, path):
        pass

    @staticmethod
    def __get_field_names():
        return ["index", "count", "completed", "incomplete",
                "deleted", "project", "timestamp"]

    @staticmethod
    def __write_row(snapshot):
        return {"index": snapshot.index, "count": snapshot.count, "completed": snapshot.completed,
                "incomplete": snapshot.incomplete,
                "deleted": snapshot.deleted,
                "project": snapshot.project,
                "timestamp": snapshot.timestamp}


class FileManager:

    @staticmethod
    def save_tasks(task_list):
        assert type(task_list) is list

        if len(task_list) > 0 and isinstance(task_list[0], Task):
            return CsvTasksFile().save(task_list)

    @staticmethod
    def open_tasks(path) -> list:
        assert type(path) is str
        return CsvTasksFile().open(path)

    @staticmethod
    def save_snapshots(snapshot_list):
        assert type(snapshot_list) is list

        if len(snapshot_list) > 0 and isinstance(snapshot_list[0], Snapshot):
            return CsvSnapshotsFile().save(snapshot_list)
