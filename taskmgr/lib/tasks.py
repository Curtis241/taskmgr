from datetime import datetime
from taskmgr.lib.task import Task


class SortType:
    Label = "label"
    Project = "project"

    @staticmethod
    def contains(value):
        return value in SortType.__dict__.values()


class Tasks(object):

    def __init__(self):
        self.__tasks = list()

    def add(self, task):
        assert type(task) is Task
        task.index = len(self.__tasks) + 1
        self.__tasks.append(task)

    def get_list(self):
        return [task for task in self.__tasks if not task.delete]

    def get_list_by_type(self, sort_type, value):
        assert SortType.contains(sort_type)
        assert type(value) == str
        return list(filter(lambda t: getattr(t, sort_type) == value, self.get_list()))

    def delete(self, task_index):
        assert type(task_index) is int
        for task in self.__tasks:
            if task.index == task_index:
                task.delete = True

    def complete(self, task_index):
        assert type(task_index) is int
        for task in self.__tasks:
            if task.index == task_index:
                task.is_complete = True

    def to_dict(self):
        return [dict(task) for task in self.get_list()]

    def sort(self, sort_type):
        assert SortType.contains(sort_type)
        return [t for t in sorted(self.get_list(), key=lambda t: getattr(t, sort_type))]

    def unique(self, sort_type):
        assert SortType.contains(sort_type)
        return set([getattr(t, sort_type) for t in self.get_list()])

    def from_dict(self, tasks_dict_list):
        "{'completed': False, 'deleted': False, 'index': 1, 'label': '', 'priority': 0, 'text': 'Task1'}"
        for task_dict in tasks_dict_list:
            task = Task(task_dict["text"])
            task.is_complete = task_dict["completed"]
            task.delete = task_dict["deleted"]
            task.index = task_dict["index"]
            task.label = task_dict["label"]
            task.project = task_dict["project"]
            task.priority = task_dict["priority"]
            task.due_date = task_dict["due_date"]
            self.add(task)
