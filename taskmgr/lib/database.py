from abc import ABC, abstractmethod
import pathlib
from pathlib import Path
import os
import yaml

from taskmgr.lib.tasks import Tasks


class Database(ABC):

    def __init__(self):
        self.tasks = Tasks()

    @abstractmethod
    def save(self, tasks): pass

    @abstractmethod
    def retrieve(self): pass


class FileDatabase(Database):

    def __init__(self):
        super().__init__()
        self.current_dir = pathlib.Path(__file__).parent

    @staticmethod
    def make_db_path(file_name):
        home = str(Path.home())
        config_dir = f"{home}/.config/taskmgr/resources/"
        path = f"{config_dir}/{file_name}.yaml"
        os.makedirs(config_dir, 0o777, exist_ok=True)
        return path

    def get_db_path(self):
        return self.make_db_path("tasks_db")

    def save(self, tasks):
        with open(self.get_db_path(), 'w') as outfile:
            tasks_dict = tasks.to_dict()
            yaml.dump(tasks_dict, outfile, default_flow_style=False)

    def retrieve(self):
        if self.exists():
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



