import ast
import re
from configparser import RawConfigParser, NoSectionError
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
        self.create_file()

    def create_file(self):
        if not Path(self.__get_file_path()).exists():
            self.cfg['DEFAULT'] = {'recurring_month_limit': 2,
                                   'default_date_expression': 'empty',
                                   'default_text_field_length': 50,
                                   'date_format': '%Y-%m-%d',
                                   'date_time_format': '%Y-%m-%d %H:%M:%S',
                                   'time_format': '%H:%M:%S',
                                   'rfc3339_date_time_format': '%Y-%m-%dT%H:%M:%S.%fZ',
                                   'file_name_timestamp': '%Y%m%d_%H%M%S',
                                   'default_project_name': '',
                                   'default_label': '',
                                   'default_text': '',
                                   'enable_redis': False,
                                   'redis_host': 'localhost',
                                   'redis_port': 6379}
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
        except NoSectionError:
            return self.cfg.get(self.default_section, key)

    def __getint(self, key, section):
        self.__read_file()
        try:
            return self.cfg.getint(section, key)
        except NoSectionError:
            return self.cfg.getint(self.default_section, key)

    def __set(self, key, value, section):
        self.__read_file()
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)
        self.cfg.set(section, key, value)
        self.__save()

    def __save(self):
        path = self.__get_file_path()
        with open(path, 'w') as configfile:
            self.cfg.write(configfile)

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
    def default_text(self):
        return self.__get("default_text", self.task_section)

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
    def default_date_expression(self):
        return self.__get("default_date_expression", self.task_section)

    @default_date_expression.setter
    def default_date_expression(self, value):
        if value is not None:
            self.__set("default_date_expression", value, self.task_section)

    @property
    def default_project_name(self):
        return self.__get("default_project_name", self.task_section)

    @default_project_name.setter
    def default_project_name(self, value):
        if value is not None:
            self.__set("default_project_name", value, self.task_section)

    @property
    def default_text_field_length(self):
        return self.__getint("default_text_field_length", self.task_section)

    @default_text_field_length.setter
    def default_text_field_length(self, value):
        if value is not None:
            self.__set("default_text_field_length", str(value), self.task_section)

    @property
    def enable_redis(self):
        return ast.literal_eval(self.__get("enable_redis", self.database_section))

    @enable_redis.setter
    def enable_redis(self, value):
        if value is not None:
            self.__set("enable_redis", str(value), self.database_section)

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

    def __iter__(self):
        yield 'default_text_field_length', self.default_text_field_length
        yield 'default_project_name', self.default_project_name
        yield 'default_label', self.default_label
        yield 'recurring_month_limit', self.recurring_month_limit
        yield 'default_date_expression', self.default_date_expression
        yield 'enable_redis', self.enable_redis
        yield 'redis_host', self.redis_host
        yield 'redis_port', self.redis_port
