from copy import deepcopy

from taskmgr.lib.date_generator import Calendar, Day, DueDate, Today
from taskmgr.lib.task import Task


class SortType:
    Label = "label"
    Project = "project"
    DueDate = "due_date"

    @staticmethod
    def contains(value):
        return value in SortType.__dict__.values()


class Tasks(object):

    def __init__(self):
        self.__tasks = list()
        self.calendar = Calendar()

    def add(self, task):
        assert type(task) is Task
        task.index = len(self.__tasks) + 1
        self.__tasks.append(task)

    def get_task_by_index(self, task_index):
        task_list = [task for task in self.__tasks if task.index == task_index]
        if len(task_list) == 1:
            return task_list[0]
        return []

    def get_task_by_name(self, task_name):
        task_list = [task for task in self.__tasks if task.text == task_name]
        if len(task_list) == 1:
            return task_list[0]
        return []

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
        task = self.get_task_by_index(task_index)
        task.complete_due_date()
        return task

    def edit(self, task_index, text, label, project, date_expression):
        task = deepcopy(self.get_task_by_index(task_index))
        task.text = text
        task.label = label
        task.project = project
        task.date_expression = date_expression
        self.__tasks[(task_index -1)] = task
        return task

    def reschedule(self, today):
        assert type(today) is Today or Day
        for task in self.get_list():
            for due_date in task.due_dates:
                if self.calendar.is_past(due_date, today) and due_date.completed is False:
                    due_date.date_string = today.to_date_string()

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
        for task_dict in tasks_dict_list:
            task = Task(task_dict["text"])
            task.delete = task_dict["deleted"]
            task.index = task_dict["index"]
            task.label = task_dict["label"]
            task.project = task_dict["project"]
            task.priority = task_dict["priority"]
            task.date_expression = task_dict["date_expression"]

            due_date_list = list()
            for due_date_dict in task_dict["due_dates"]:
                d = DueDate()
                d.date_string = due_date_dict["date_string"]
                d.completed = due_date_dict["completed"]
                due_date_list.append(d)

            task.due_dates = due_date_list
            self.add(task)
