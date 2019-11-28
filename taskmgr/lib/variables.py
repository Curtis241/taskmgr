from configparser import RawConfigParser, NoSectionError
from pathlib import Path


class CommonVariables:

    def __init__(self):
        self.task_section = "task"
        self.default_section = "DEFAULT"
        self.ini_file = "variables.ini"
        self.cfg = RawConfigParser()
        self.home_dir = Path.home()

    def __get_file_path(self):
        current_dir = str(Path(__file__)).rsplit("/", 1)[0]
        return f"{current_dir}/{self.ini_file}"

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

    def __iter__(self):
        yield 'default_text_field_length', self.default_text_field_length
        yield 'default_project_name', self.default_project_name
        yield 'default_label', self.default_label
        yield 'recurring_month_limit', self.recurring_month_limit
        yield 'default_date_expression', self.default_date_expression
