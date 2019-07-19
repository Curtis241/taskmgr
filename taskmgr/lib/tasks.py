import uuid
from copy import deepcopy
from datetime import datetime

from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.date_generator import Calendar, Day, DueDate, Today
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task import Task


class TaskKeyError(IndexError):
    logger = AppLogger("task_key_error").get_logger()
    msg = "task.key cannot be found"

    def __init__(self):
        super().__init__(self.msg)
        self.logger.error(self.msg)


class SortType:
    Complete = 'complete'
    Incomplete = "incomplete"
    Label = "label"
    Project = "project"
    DueDate = "due_date"

    @staticmethod
    def contains(value):
        return value in SortType.__dict__.values()


class TaskItem:

    def __init__(self, index, task):
        self.index = index
        self.task = task


class Tasks(object):
    logger = AppLogger("tasks").get_logger()

    def __init__(self, file_database=None):
        self.__calendar = Calendar()

        if file_database is not None:
            self.__db = file_database
        else:
            self.__db = JsonFileDatabase()

        self.__tasks = list()
        self.retrieve()

    def save(self):
        self.__db.save(self.to_dict())

    def retrieve(self):
        tasks_dict_list = self.__db.retrieve()
        if tasks_dict_list is not None:
            self.__tasks = list()
            self.__tasks = self.from_dict(tasks_dict_list)

    def add(self, task):
        assert type(task) is Task
        task.id = uuid.uuid4().hex
        task.deleted = False
        task.key = str(task.id)[-3:]
        task.last_updated = self.get_date_time_string()
        self.logger.debug(f"added {dict(task)}")
        self.__tasks.append(task)
        self.save()
        return task

    def get_task(self, func) -> TaskItem:
        for index, task in enumerate(self.__tasks):
            if func(task) is not None:
                self.logger.debug(f"Retrieved task by index: {index}, text: {task.text}")
                return TaskItem(index, task)

    def get_task_by_key(self, key) -> TaskItem:
        assert type(key) is str
        return self.get_task(lambda task: task if task.key == key else None)

    def get_task_by_external_id(self, external_id) -> TaskItem:
        assert type(external_id) is str
        return self.get_task(lambda task: task if task.external_id == external_id else None)

    def get_task_by_id(self, task_id) -> TaskItem:
        assert type(task_id) is str
        return self.get_task(lambda task: task if task.id == task_id else None)

    def get_task_by_name(self, task_name) -> TaskItem:
        assert type(task_name) is str
        return self.get_task(lambda task: task if task.text == task_name else None)

    def get_list_by_type(self, sort_type, value):
        assert SortType.contains(sort_type)
        assert type(value) == str
        return list(filter(lambda t: getattr(t, sort_type) == value, self.get_list()))

    def get_list(self):
        return self.__tasks

    def delete(self, key) -> Task:
        assert type(key) is str

        item = self.get_task_by_key(key)
        if item.task is not None:
            self.logger.debug(f"Deleting {dict(item.task)}")
            item.task.last_updated = self.get_date_time_string()
            item.task.deleted = True
            self.__tasks[item.index] = item.task
            self.save()
            return item.task
        else:
            raise TaskKeyError()

    def complete(self, key) -> Task:
        assert type(key) is str

        item = self.get_task_by_key(key)
        if item.task is not None:
            item.task.last_updated = self.get_date_time_string()
            item.task.complete()
            self.__tasks[item.index] = item.task
            self.save()
            return item.task
        else:
            raise TaskKeyError()

    def replace(self, task) -> Task:
        assert type(task) is Task

        self.logger.debug(f"Attempting to replace task {dict(task)}")
        item = TaskItem(0, None)
        if type(task.external_id) is str and len(task.external_id) > 0:
            item = deepcopy(self.get_task_by_external_id(task.external_id))
        elif type(task.id) is str and len(task.id) > 0:
            item = deepcopy(self.get_task_by_id(task.id))

        if item.task is not None:
            item.task.id = item.task.id
            item.task.key = item.task.key
            item.task.deleted = False
            item.task.last_updated = self.get_date_time_string()
            self.__tasks[item.index] = item.task
            return item.task
        else:
            msg = "task.external_id or task.id is required"
            self.logger.error(msg)
            raise AttributeError(msg)

    def edit(self, key, text, label, project, date_expression) -> Task:
        item = deepcopy(self.get_task_by_key(key))
        if item.task is not None:
            item.task.text = text
            item.task.label = label
            item.task.project = project
            item.task.date_expression = date_expression
            item.task.last_updated = self.get_date_time_string()
            self.__tasks[item.index] = item.task
            self.save()
            return item.task
        else:
            raise TaskKeyError()

    def reschedule(self, today) -> None:
        assert type(today) is Today or Day
        for task in self.get_list():
            for due_date in task.due_dates:
                if self.__calendar.is_past(due_date, today) and due_date.completed is False:
                    task.last_updated = self.get_date_time_string()
                    due_date.date_string = today.to_date_string()
        self.save()

    def clear(self):
        self.__tasks = []

    def to_dict(self):
        return [dict(task) for task in self.get_list()]

    def sort(self, sort_type):
        assert SortType.contains(sort_type)
        return [t for t in sorted(self.get_list(), key=lambda t: getattr(t, sort_type))]

    def unique(self, sort_type):
        assert SortType.contains(sort_type)
        return set([getattr(t, sort_type) for t in self.get_list()])

    def from_dict(self, tasks_dict_list):
        assert type(tasks_dict_list) is list

        for task_dict in tasks_dict_list:
            task = Task(getattr(task_dict, "text", str()))
            for key, value in task_dict.items():
                if type(value) is list:
                    task.due_dates = [DueDate().from_dict(due_date_dict) for due_date_dict in value]
                else:
                    setattr(task, key, value)
            self.__tasks.append(task)
        return self.__tasks

    @staticmethod
    def get_date_time_string() -> str:
        return Day(datetime.now()).to_date_time_string()
