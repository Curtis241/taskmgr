import os
from abc import ABC, abstractmethod

import ujson
import yaml

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class Database(ABC):
    """Generic base class to support Yaml and Json file databases. I chose a file db instead
    of a database such as MySql, Postgres, etc to keep client as light weight as possible. I don't want more
    then 100 tasks at any time because it would be too hard to manage priorities. The Google tasks service
    is really the persistent storage for this app so no need to make it complex by adding an external db."""
    logger = AppLogger("database").get_logger()

    def __init__(self, db_name, ext):

        resources_dir = CommonVariables().resources_dir
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
    """
    Manages saving and retrieving tasks as dict object to a json file
    located in the resource directory.
    """
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
    """
    Manages saving and retrieving tasks as dict object to a yaml file
    located in the resource directory.
    """
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
