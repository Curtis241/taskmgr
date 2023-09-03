import csv
import os
import time
from abc import abstractmethod
from operator import attrgetter
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.model.task import Task
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.variables import CommonVariables


class UnmatchedColumns(Exception):
    pass


class File:
    logger = AppLogger("file").get_logger()

    def __init__(self):
        if len(CommonVariables().export_dir) > 0:
            self.__output_dir = CommonVariables().export_dir
        else:
            self.__output_dir = CommonVariables().resources_dir

    @staticmethod
    def get_timestamp():
        return time.strftime(CommonVariables().file_name_timestamp)

    def open(self, path: str, field_names: list):
        obj_list = list()
        if os.path.exists(path):
            self.logger.info(f"Reading file {path}")
            with open(path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                if set(reader.fieldnames) == set(field_names):
                    for row in reader:
                        obj_list.append(row)
                else:
                    raise UnmatchedColumns(f"Found unexpected column(s) in csv file")

            return obj_list
        else:
            raise FileNotFoundError(f"Path {path} does not exist")

    def save(self, file_name: str, obj_list: list, field_names: list, row_func) -> str:

        if os.path.exists(self.__output_dir):
            path = self.__make_path(self.__output_dir, file_name)
            with open(path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                for obj in sorted(obj_list, key=attrgetter('index')):
                    writer.writerow(row_func(obj))

            self.logger.info(f"Saved results to {path}")
            return path
        else:
            raise FileNotFoundError(f"{self.__output_dir} directory does not exist")

    @staticmethod
    def __make_path(file_path, file_name) -> str:
        if str(file_path).endswith("/"):
            path = f"{file_path}{file_name}"
        else:
            path = f"{file_path}/{file_name}"
        return path

    @abstractmethod
    def write_file(self, obj_list):
        pass

    @abstractmethod
    def read_file(self, path):
        pass

    @abstractmethod
    def get_filename(self):
        pass


class CsvTasksFile(File):

    logger = AppLogger("csv_tasks_file").get_logger()

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"tasks_{self.get_timestamp()}.csv"

    def write_file(self, task_list: List[Task]):
        self.save(self.get_filename(), task_list,
                  self.get_field_names(), self.write_row)

    def read_file(self, path: str):
        return self.open(path, self.get_field_names())

    @staticmethod
    def get_field_names():
        return ["index", "done", "name", "project", "label", "time_spent", "due_date",
                "last_updated", "deleted", "unique_id"]

    @staticmethod
    def write_row(task):
        return {"index": task.index,
                "done": task.completed,
                "name": task.name,
                "project": task.project,
                "label": task.label,
                "time_spent": task.time_spent,
                "due_date": task.due_date,
                "last_updated": task.last_updated,
                "deleted": task.deleted,
                "unique_id": task.unique_id}

class CsvTimeCardsFile(File):

    logger = AppLogger("csv_time_cards_file").get_logger()

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"time_cards_{self.get_timestamp()}.csv"

    def write_file(self, time_card_list: List[TimeCard]):
        self.save(self.get_filename(), time_card_list,
                  self.get_field_names(), self.write_row)

    def read_file(self, path):
        return self.open(path, self.get_field_names())

    @staticmethod
    def get_field_names():
        return ["index", "date", "time_in", "time_out", "unique_id", "deleted"]

    @staticmethod
    def write_row(time_card):
        return {"index": time_card.index,
                "date": time_card.date,
                "time_in": time_card.time_in,
                "time_out": time_card.time_out,
                "unique_id": time_card.unique_id,
                "deleted": time_card.deleted
                }

class CsvSnapshotsFile(File):

    def __init__(self):
        super().__init__()

    def get_filename(self):
        return f"snapshots_{self.get_timestamp()}.csv"

    def write_file(self, snapshot_list: List[Snapshot]):
        self.save(self.get_filename(), snapshot_list,
                  self.get_field_names(), self.write_row)

    def read_file(self, path):
        pass

    @staticmethod
    def get_field_names():
        return ["index", "count", "completed", "incomplete",
                "deleted", "total_time", "due_date"]

    @staticmethod
    def write_row(snapshot):
        return {"due_date": snapshot.due_date, "index": snapshot.index,
                "count": snapshot.task_count, "completed": snapshot.complete_count,
                "incomplete": snapshot.incomplete_count,
                "deleted": snapshot.delete_count,
                "total_time": snapshot.total_time
                }


class FileManager:

    logger = AppLogger("file_manager").get_logger()

    @staticmethod
    def save_tasks(task_list: List[Task]):
        assert type(task_list) is list
        if len(task_list) > 0:
            return CsvTasksFile().write_file(task_list)
        else:
            FileManager.logger.info("Cannot export empty list")

    @staticmethod
    def open_tasks(path: str) -> list:
        assert type(path) is str
        return CsvTasksFile().read_file(path)

    @staticmethod
    def save_snapshots(snapshot_list: List[Snapshot]):
        assert type(snapshot_list) is list
        if len(snapshot_list) > 0:
            return CsvSnapshotsFile().write_file(snapshot_list)
        else:
            FileManager.logger.info("Cannot export empty list")

    @staticmethod
    def open_time_cards(path: str) -> list:
        assert type(path) is str
        return CsvTimeCardsFile().read_file(path)
    @staticmethod
    def get_time_card_columns():
        return CsvTimeCardsFile().get_field_names()

    @staticmethod
    def get_task_columns():
        return CsvTasksFile().get_field_names()

    @staticmethod
    def save_time_cards(time_card_list: List[TimeCard]):
        assert type(time_card_list) is list
        if len(time_card_list) > 0:
            return CsvTimeCardsFile().write_file(time_card_list)
        else:
            FileManager.logger.info("Cannot export empty list")
