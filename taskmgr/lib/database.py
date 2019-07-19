import os
import pathlib
from abc import ABC, abstractmethod


import yaml
import ujson

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class Database(ABC):
    logger = AppLogger("database").get_logger()

    def __init__(self):
        self.db_name = "tasks_db"

    def make_db_path(self, file_name):
        resources_dir = CommonVariables.resources_dir
        ext = self.get_ext()
        path = f"{resources_dir}/{file_name}.{ext}"
        os.makedirs(resources_dir, 0o777, exist_ok=True)
        return path

    def get_db_path(self):
        return self.make_db_path(self.db_name)

    @abstractmethod
    def save(self, obj_list):
        pass

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def get_ext(self):
        pass

    def exists(self):
        return os.path.exists(self.get_db_path())

    def remove(self):
        path = self.get_db_path()
        try:
            os.remove(path)
        except Exception as ex:
            self.logger.error(f"Cannot remove database file {path}")


class JsonFileDatabase(Database):
    logger = AppLogger("json_file_database").get_logger()

    def __init__(self, db_name=None):
        super().__init__()
        if db_name is not None:
            self.db_name = db_name

    def save(self, obj_list):
        assert type(obj_list) is list
        if not self.exists():
            self.make_db_path(self.db_name)
        with open(self.get_db_path(), 'w') as outfile:
            self.logger.debug("Saved json database")
            ujson.dump(obj_list, outfile)

    def retrieve(self):
        if not self.exists():
            self.make_db_path(self.db_name)
        else:
            self.logger.debug("Retrieved json database")
            with open(self.get_db_path(), 'r') as infile:
                return ujson.load(infile)

    def get_ext(self):
        return "json"


class YamlFileDatabase(Database):
    logger = AppLogger("yaml_file_database").get_logger()

    def __init__(self, db_name=None):
        super().__init__()

        if db_name is not None:
            self.db_name = db_name

    def save(self, obj_list):
        assert type(obj_list) is list
        with open(self.get_db_path(), 'w') as outfile:
            self.logger.debug("Saved yaml database")
            yaml.dump(obj_list, outfile, default_flow_style=False)

    def retrieve(self):
        if not self.exists():
            self.make_db_path(self.db_name)
        else:
            self.logger.debug("Retrieved yaml database")
            with open(self.get_db_path(), 'r') as infile:
                return yaml.load(infile)

    def get_ext(self):
        return "yaml"
