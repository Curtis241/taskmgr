from abc import ABC, abstractmethod

import pathlib
import yaml
import os

from taskmgr.lib.tasks import Tasks


class Database(ABC):

    def __init__(self):
        self.__tasks = Tasks()
        self.current_dir = pathlib.Path(__file__).parent

    def make_db_path(self, file_name):
        return f"{self.current_dir}/resources/{file_name}.yaml"

    @abstractmethod
    def get_db_path(self): pass

    def save(self, tasks):
        with open(self.get_db_path(), 'w') as outfile:
            tasks_dict = tasks.to_dict()
            yaml.dump(tasks_dict, outfile, default_flow_style=False)

    def retrieve(self):
        if os.path.exists(self.get_db_path()):
            with open(self.get_db_path(), 'r') as infile:
                tasks_dict = yaml.load(infile)
                self.__tasks.from_dict(tasks_dict)
                return self.__tasks
        else:
            return self.__tasks

    def remove(self):
        try:
            os.remove(self.get_db_path())
        except:
            pass


class FileDatabase(Database):

    def get_db_path(self):
        return self.make_db_path("tasks_db")



