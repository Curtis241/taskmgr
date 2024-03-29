import os
import re
from configparser import RawConfigParser, NoSectionError, NoOptionError
from pathlib import Path


class CommonVariables:

    def __init__(self, ini_file_name=None):
        self.task_section = "task"
        self.database_section = "database"
        self.default_section = "DEFAULT"

        if ini_file_name is None:
            self.ini_file = "variables.ini"
        else:
            self.ini_file = ini_file_name

        self.cfg = RawConfigParser()
        self.cfg['DEFAULT'] = {'recurring_month_limit': 2,
                               'default_name_field_length': 50,
                               'date_format': '%Y-%m-%d',
                               'date_time_format': '%Y-%m-%d %H:%M:%S',
                               'time_format': '%H:%M:%S',
                               'rfc3339_date_time_format': '%Y-%m-%dT%H:%M:%S.%fZ',
                               'file_name_timestamp': '%Y%m%d_%H%M%S',
                               'default_project_name': '',
                               'default_label': '',
                               'default_name': '',
                               'redis_host': 'localhost',
                               'redis_port': 6379,
                               'redis_username': 'Unset',
                               'redis_password': 'Unset',
                               'export_dir': '',
                               'max_rows': 10}
        self.create_file()

    def create_file(self):
        if not Path(self.__get_file_path()).exists():
            os.makedirs(self.resources_dir, exist_ok=True)
            self.__save()

    def __get_file_path(self):
        return f"{self.resources_dir}/{self.ini_file}"

    def __read_file(self):
        path = self.__get_file_path()
        with open(path, 'r') as configfile:
            self.cfg.read_file(configfile)

    def __get(self, key, section):
        self.__read_file()
        try:
            return self.cfg.get(section, key)
        except NoSectionError or NoOptionError:
            self.__delete()
            self.create_file()
            return self.cfg.get(self.default_section, key)

    def __getint(self, key, section):
        self.__read_file()
        try:
            return self.cfg.getint(section, key)
        except NoSectionError or NoOptionError:
            self.__delete()
            self.create_file()
            return self.cfg.getint(self.default_section, key)

    def __set(self, key, value, section):
        self.__read_file()
        if section is not self.default_section and self.cfg.has_section(section) is False:
            self.cfg.add_section(section)
        self.cfg.set(section, key, value)
        self.__save()

    def __save(self):
        path = self.__get_file_path()
        with open(path, 'w') as configfile:
            self.cfg.write(configfile)

    def __delete(self):
        try:
            os.remove(self.__get_file_path())
        except FileExistsError:
            pass

    def reset(self):
        self.cfg.clear()
        path = self.__get_file_path()
        with open(path, 'w') as configfile:
            self.cfg.write(configfile)

    @property
    def log_dir(self):
        return f"{Path.home()}/.config/taskmgr/log/"

    @property
    def credentials_dir(self):
        return f"{Path.home()}/.config/taskmgr/credentials/"

    @property
    def resources_dir(self):
        return f"{Path.home()}/.config/taskmgr/resources/"

    @property
    def date_format(self):
        return self.__get("date_format", self.default_section)

    @staticmethod
    def validate_date_format(date_string:str) -> bool:
        return re.match(r'^\d{4}-\d{2}-\d{2}$', date_string) is not None

    @property
    def date_time_format(self):
        return self.__get("date_time_format", self.default_section)

    @property
    def time_format(self):
        return self.__get("time_format", self.default_section)

    @property
    def rfc3339_date_time_format(self):
        return self.__get("rfc3339_date_time_format", self.default_section)

    @property
    def file_name_timestamp(self):
        return self.__get("file_name_timestamp", self.default_section)

    @property
    def max_rows(self):
        return self.__getint("max_rows", self.default_section)

    @max_rows.setter
    def max_rows(self, value):
        if value is not None:
            self.__set("max_rows", int(value), self.default_section)

    @property
    def default_name(self):
        return self.__get("default_name", self.task_section)

    @property
    def default_label(self):
        return self.__get("default_label", self.task_section)

    @default_label.setter
    def default_label(self, value):
        if value is not None:
            self.__set("default_label", value, self.task_section)

    @property
    def recurring_month_limit(self):
        return self.__getint("recurring_month_limit", self.task_section)

    @recurring_month_limit.setter
    def recurring_month_limit(self, value):
        if value is not None:
            self.__set("recurring_month_limit", value, self.task_section)

    @property
    def default_project_name(self):
        return self.__get("default_project_name", self.task_section)

    @default_project_name.setter
    def default_project_name(self, value):
        if value is not None:
            self.__set("default_project_name", value, self.task_section)

    @property
    def default_name_field_length(self):
        return self.__getint("default_name_field_length", self.task_section)

    @default_name_field_length.setter
    def default_name_field_length(self, value):
        if value is not None:
            self.__set("default_name_field_length", str(value), self.task_section)

    @property
    def redis_host(self):
        return self.__get("redis_host", self.database_section)

    @redis_host.setter
    def redis_host(self, value):
        if value is not None:
            self.__set("redis_host", str(value), self.database_section)

    @property
    def redis_port(self):
        return self.__getint("redis_port", self.database_section)

    @redis_port.setter
    def redis_port(self, value):
        if value is not None:
            self.__set("redis_port", int(value), self.database_section)

    @property
    def redis_username(self):
        return self.__get("redis_username", self.database_section)

    @redis_username.setter
    def redis_username(self, value):
        if value is not None:
            self.__set("redis_username", str(value), self.database_section)

    @property
    def redis_password(self):
        return self.__get("redis_password", self.database_section)

    @redis_password.setter
    def redis_password(self, value):
        if value is not None:
            self.__set("redis_password", str(value), self.database_section)

    @property
    def export_dir(self):
        return self.__get("export_dir", self.default_section)

    @export_dir.setter
    def export_dir(self, value):
        if value is not None:
            self.__set("export_dir", str(value), self.default_section)

    def __iter__(self):
        yield 'default_name_field_length', self.default_name_field_length
        yield 'default_project_name', self.default_project_name
        yield 'default_label', self.default_label
        yield 'recurring_month_limit', self.recurring_month_limit
        yield 'redis_host', self.redis_host
        yield 'redis_port', self.redis_port
        yield 'redis_username', self.redis_username
        yield 'redis_password', "***********"
        yield 'export_dir', self.export_dir
        yield 'max_rows', self.max_rows

