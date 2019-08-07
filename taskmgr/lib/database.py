import os
from abc import ABC, abstractmethod

import ujson
import yaml

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class Database(ABC):
    logger = AppLogger("database").get_logger()

    def __init__(self, db_name, ext):

        resources_dir = CommonVariables.resources_dir
        self.path = f"{resources_dir}{db_name}.{ext}"

        if not self.exists():
            os.makedirs(resources_dir, 0o777, exist_ok=True)

    @abstractmethod
    def save(self, obj_list):
        pass

    @abstractmethod
    def retrieve(self):
        pass

    def exists(self):
        return os.path.exists(self.path)

    def remove(self):
        try:
            if self.exists():
                os.remove(self.path)
        except FileNotFoundError as ex:
            self.logger.error(f"Cannot remove database file {ex}")
            raise


class JsonFileDatabase(Database):
    logger = AppLogger("json_file_database").get_logger()

    def __init__(self, db_name):
        super().__init__(db_name, 'json')

    def save(self, obj_list):
        assert type(obj_list) is list
        with open(self.path, 'w') as outfile:
            self.logger.debug("Saved json database")
            ujson.dump(obj_list, outfile)

    def retrieve(self):
        if self.exists():
            self.logger.debug("Retrieved json database")
            with open(self.path, 'r') as infile:
                return ujson.load(infile)


class YamlFileDatabase(Database):
    logger = AppLogger("yaml_file_database").get_logger()

    def __init__(self, db_name):
        super().__init__(db_name, 'yaml')

    def save(self, obj_list):
        assert type(obj_list) is list
        with open(self.path, 'w') as outfile:
            self.logger.debug("Saved yaml database")
            yaml.dump(obj_list, outfile, default_flow_style=False)

    def retrieve(self):
        if self.exists():
            self.logger.debug("Retrieved yaml database")
            with open(self.path, 'r') as infile:
                return yaml.load(infile)
