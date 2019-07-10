import os
import pathlib
from abc import ABC, abstractmethod


import yaml

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class Database(ABC):

    def __init__(self):
        self.current_dir = pathlib.Path(__file__).parent

    @staticmethod
    def make_db_path(file_name):
        resources_dir = CommonVariables.resources_dir
        path = f"{resources_dir}/{file_name}.yaml"
        os.makedirs(resources_dir, 0o777, exist_ok=True)
        return path

    @abstractmethod
    def get_db_path(self): pass

    @abstractmethod
    def save(self, obj): pass

    @abstractmethod
    def retrieve(self): pass

    @abstractmethod
    def exists(self): pass

    @abstractmethod
    def remove(self): pass


class FileDatabase(Database):
    logger = AppLogger("file_database").get_logger()

    def __init__(self, db_name="tasks_db"):
        super().__init__()
        self.tasks = Tasks()
        self.db_name = db_name

    def get_db_path(self):
        return self.make_db_path(self.db_name)

    def save(self, obj):
        with open(self.get_db_path(), 'w') as outfile:
            self.logger.debug("Saved database")
            tasks_dict = obj.to_dict()
            yaml.dump(tasks_dict, outfile, default_flow_style=False)

    def retrieve(self):

        if not self.exists():
            self.make_db_path(self.db_name)

        if self.exists():
            self.logger.debug("Retrieved database")
            with open(self.get_db_path(), 'r') as infile:
                tasks_dict = yaml.load(infile)
                self.tasks.from_dict(tasks_dict)
                return self.tasks
        else:
            return self.tasks

    def exists(self):
        return os.path.exists(self.get_db_path())

    def remove(self):
        try:
            os.remove(self.get_db_path())
        except:
            pass


class SyncDatabase(Database):

    def __init__(self):
        super().__init__()
        self.sync_list = SyncList()

    def get_db_path(self):
        return self.make_db_path("sync_db")

    def save(self, obj):
        with open(self.get_db_path(), 'w') as outfile:
            sync_dict = obj.to_dict()
            yaml.dump(sync_dict, outfile, default_flow_style=False)

    def retrieve(self):
        if self.exists():
            with open(self.get_db_path(), 'r') as infile:
                sync_dict = yaml.load(infile)
                self.sync_list.from_dict(sync_dict)
                return self.sync_list
        else:
            return self.sync_list

    def exists(self):
        return os.path.exists(self.get_db_path())

    def remove(self):
        try:
            os.remove(self.get_db_path())
        except:
            pass
