from datetime import datetime
from typing import Set, List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.task import Task

from taskmgr.lib.model.calendar import Calendar, Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.presenter.date_generator import DateGenerator

from taskmgr.lib.variables import CommonVariables


class TaskKeyError(IndexError):
    logger = AppLogger("task_key_error").get_logger()
    msg = "task.key cannot be found"

    def __init__(self):
        super().__init__(self.msg)
        self.logger.error(self.msg)


class Tasks(Model):
    """
    Main entry point for querying and managing local tasks.
    """
    logger = AppLogger("tasks").get_logger()

    def __init__(self, database):
        super().__init__(database, Task())
        self.__calendar = Calendar()
        self.__vars = CommonVariables()
        self.__date_generator = DateGenerator()

    def add(self, text, label, project, date_expression) -> List[Task]:
        assert type(text) and type(label) and type(project)\
               and type(date_expression) is str
        task_list = list()
        if self.__date_generator.validate_input(date_expression):
            for due_date in self.__date_generator.get_due_dates(date_expression):
                task = Task(text)
                task.label = label
                task.project = project
                task.date_expression = date_expression
                task.due_date = due_date
                self.append(task)
                task_list.append(task)
        else:
            raise AttributeError(f"Provided due date {date_expression} is invalid")

        return task_list

    def append(self, obj: Task):
        assert isinstance(obj, Task)
        return self.append_object(obj)

    def contains_due_date_range(self, task, min_date_string, max_date_string):
        assert isinstance(task, Task)
        assert type(min_date_string) and type(max_date_string) is str

        min_day = Day(datetime.strptime(min_date_string, self.__vars.date_format))
        max_day = Day(datetime.strptime(max_date_string, self.__vars.date_format))
        if len(task.due_date.date_string) > 0:
            day = Day(datetime.strptime(task.due_date.date_string, self.__vars.date_format))

            if min_day.to_date_time() < day.to_date_time() < max_day.to_date_time():
                return task

    def get_task(self, func) -> Task:
        for task in self.get_object_list():
            if func(task) is not None:
                self.logger.debug(f"Retrieved task by index: {task.index}, text: {task.text}")
                return task

    def get_task_list(self):
        return sorted(self.get_object_list(), key=lambda task: task.due_date.date_string)

    def get_tasks_containing_text(self, value) -> List[Task]:
        """
        Selects all tasks that with a text value that contain the provided value
        :param value:
        :return: list of Task
        """
        assert type(value) is str
        return [task for task in self.get_task_list()
                if str(value).lower() in str(task.text).lower()]

    def get_tasks_matching_text(self, value) -> List[Task]:
        """
        Selects all tasks with a text value that matches the provided value
        :param value:
        :return:
        """
        assert type(value) is str
        return [task for task in self.get_task_list()
                if str(value.lower() == str(task.text).lower())]

    def get_task_by_index(self, index: int) -> Task:
        assert type(index) is int
        return self.get_task(lambda task: task if task.index == index else None)

    def get_task_by_external_id(self, external_id: int) -> Task:
        assert type(external_id) is str
        return self.get_task(lambda task: task if task.external_id == external_id else None)

    def get_task_by_id(self, task_id: str) -> Task:
        assert type(task_id) is str
        return self.get_task(lambda task: task if task.unique_id == task_id else None)

    def get_task_by_name(self, task_name: str) -> Task:
        assert type(task_name) is str
        return self.get_task(lambda task: task if task.text == task_name else None)

    def get_tasks_by_date(self, date_expression: str) -> List[Task]:
        assert type(date_expression) is str
        task_list = list()
        for due_date in self.__date_generator.get_due_dates(date_expression):
            for task in self.get_task_list():
                if task.due_date.date_string == due_date.date_string:
                    task_list.append(task)
        return task_list

    def get_tasks_within_date_range(self, min_date_string: str, max_date_string: str) -> List[Task]:
        assert type(min_date_string) is str
        assert type(max_date_string) is str
        return [task for task in self.get_task_list()
                if self.contains_due_date_range(task, min_date_string, max_date_string)]

    def get_tasks_by_status(self, is_completed: bool) -> List[Task]:
        assert type(is_completed) is bool

        if is_completed:
            return [task for task in self.get_task_list() if task.is_completed()]
        else:
            return [task for task in self.get_task_list() if not task.is_completed()]

    def get_tasks_by_project(self, project: str) -> List[Task]:
        assert type(project) is str
        return self.get_list_by_type("project", project)

    def get_tasks_by_label(self, label: str) -> List[Task]:
        assert type(label) is str
        return self.get_list_by_type("label", label)

    def get_filtered_list(self) -> List[Task]:
        return [task for task in self.get_task_list() if not task.deleted]

    def delete(self, task_id: str) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.deleted = True
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def undelete(self, task_id: str) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.deleted = False
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def complete(self, task_id: str) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.complete()
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def reset(self, task_id: str) -> Task:
        """
        Resets the due date to today on the selected task
        :param task_id:
        :return:
        """
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            due_date = DueDate()
            due_date.completed = False
            due_date.date_string = Today().to_date_string()
            task.due_date = due_date
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def replace(self, local_task: Task, remote_task: Task) -> Task:
        assert isinstance(remote_task, Task)
        assert isinstance(local_task, Task)

        remote_task.index = local_task.index
        remote_task.unique_id = local_task.unique_id
        remote_task.due_date = local_task.due_date

        self.replace_object(local_task.index, remote_task)
        self.logger.debug(f"Replaced local_task: {dict(local_task)} with remote_task: {dict(remote_task)}")
        return remote_task

    def edit(self, index: int, text: str, label: str, project: str, date_expression: str) -> Task:

        task = self.get_task_by_index(index)
        if task is not None:
            task.text = text
            task.project = project
            task.label = label

            due_date = self.__date_generator.get_due_date(date_expression)
            if due_date is not None:
                task.date_expression = date_expression
                task.due_date.date_string = due_date.date_string

            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def reschedule(self, today) -> None:
        assert type(today) is Today or Day
        task_list = self.get_task_list()
        for task in task_list:
            if self.__calendar.is_past(task.due_date, today) and task.due_date.completed is False:
                task.due_date.date_string = today.to_date_string()
        self.update_objects(task_list)

    def get_list_by_type(self, parameter_name: str, value: str, task_list=None) -> list:
        """
        Returns list of tasks when a task parameter (ie. project, text, label) matches
        a single value.
        :param parameter_name:
        :param value:
        :param task_list:
        :return:
        """
        assert type(parameter_name) is str
        assert type(value) is str

        if task_list is None:
            task_list = self.get_task_list()
        else:
            assert type(task_list) is list

        return list(filter(lambda t: getattr(t, parameter_name) == value, task_list))

    def __sort(self, parameter_name: str) -> list:
        assert type(parameter_name) is str
        return [t for t in sorted(self.get_task_list(), key=lambda t: getattr(t, parameter_name))]

    def get_label_set(self) -> Set[Task]:
        return self.unique("label", self.get_task_list())

    def get_project_set(self) -> Set[Task]:
        return self.unique("project", self.get_task_list())

    def get_due_date_set(self) -> Set[Task]:
        return set([task.due_date.date_string for task in self.get_task_list()])

    @staticmethod
    def unique(parameter_name: str, task_list: list) -> Set[Task]:
        assert type(parameter_name) is str
        assert type(task_list) is list
        return set([getattr(task, parameter_name) for task in task_list])

    def clear(self):
        self.clear_objects()
