from datetime import datetime
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Calendar, Today
from taskmgr.lib.model.day import Day
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import DateGenerator
from taskmgr.lib.variables import CommonVariables


class TaskKeyError(IndexError):
    logger = AppLogger("task_key_error").get_logger()
    msg = "task.key cannot be found"

    def __init__(self):
        super().__init__(self.msg)
        self.logger.error(self.msg)


class DueDateError(Exception):
    logger = AppLogger("due_date_error").get_logger()


class Tasks:
    """
    Main entry point for querying and managing local tasks.
    """
    logger = AppLogger("tasks").get_logger()

    def __init__(self, database):
        self.__db = database
        self.__calendar = Calendar()
        self.__vars = CommonVariables()
        self.__date_generator = DateGenerator()

    def add(self, name: str, label: str, project: str, date_expression: str) -> List[Task]:

        if not date_expression:
            raise DueDateError(f"Provided due date {date_expression} is empty")

        task_list = list()
        if self.__date_generator.validate_input(date_expression):
            for due_date in self.__date_generator.get_due_dates(date_expression):
                task = Task(name)
                task.label = label
                task.project = project
                task.due_date = due_date.date_string
                task.due_date_timestamp = due_date.to_timestamp()
                task.completed = False
                self.__db.append_object(task)
                task_list.append(task)
        else:
            raise DueDateError(f"Provided due date {date_expression} is invalid")

        return task_list

    def contains_due_date_range(self, task: Task, min_date_string: str, max_date_string: str):
        assert isinstance(task, Task)
        assert type(min_date_string) and type(max_date_string) is str

        min_day = Day(datetime.strptime(min_date_string, self.__vars.date_format))
        max_day = Day(datetime.strptime(max_date_string, self.__vars.date_format))
        if len(task.due_date) > 0:
            day = Day(datetime.strptime(task.due_date, self.__vars.date_format))

            if min_day.to_date_time() < day.to_date_time() < max_day.to_date_time():
                return task

    def get_task(self, func) -> Task:
        for task in self.__db.get_object_list():
            if func(task) is not None:
                self.logger.debug(f"Retrieved task by index: {task.index}, name: {task.name}")
                return task

    def get_task_list(self):
        return sorted(self.__db.get_object_list(), key=lambda task: task.due_date)

    def get_tasks_containing_name(self, value: str) -> List[Task]:
        """
        Selects all tasks that with a name value that contain the provided value
        :param value:
        :return: list of Task
        """
        assert type(value) is str
        return [task for task in self.get_task_list()
                if str(value).lower() in str(task.name).lower()]

    def get_tasks_matching_name(self, value: str) -> List[Task]:
        """
        Selects all tasks with a name value that matches the provided value
        :param value:
        :return:
        """
        assert type(value) is str
        return [task for task in self.get_task_list()
                if str(value).lower() == str(task.name).lower()]

    def get_task_by_index(self, index: int) -> Task:
        assert type(index) is int
        return self.get_task(lambda task: task if task.index == index else None)

    def get_task_by_id(self, task_id: str) -> Task:
        assert type(task_id) is str
        return self.get_task(lambda task: task if task.unique_id == task_id else None)

    def get_task_by_name(self, task_name: str) -> Task:
        assert type(task_name) is str
        return self.get_task(lambda task: task if task.name == task_name else None)

    def get_tasks_by_date(self, date_expression: str) -> List[Task]:
        assert type(date_expression) is str
        task_list = list()
        for due_date in self.__date_generator.get_due_dates(date_expression):
            for task in self.get_task_list():
                if task.due_date == due_date.date_string:
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
            return [task for task in self.get_task_list() if task.completed]
        else:
            return [task for task in self.get_task_list() if not task.completed]

    def get_tasks_by_project(self, project: str) -> List[Task]:
        assert type(project) is str
        return self.get_list_by_type("project", project)

    def get_tasks_by_label(self, label: str) -> List[Task]:
        assert type(label) is str
        return self.get_list_by_type("label", label)

    def get_filtered_list(self) -> List[Task]:
        return [task for task in self.get_task_list() if not task.deleted]

    def delete(self, task: Task, save: bool = True) -> Task:
        """
        Changes the deleted state to True
        :param task: Task object
        :param save: Persists the object to redis when True
        :return: Task object
        """
        assert isinstance(task, Task)
        if task is not None:
            task.deleted = True
            if save:
                return self.__db.replace_object(task)
            else:
                return task
        else:
            raise TaskKeyError()

    def undelete(self, task: Task) -> Task:
        """
        Changes the deleted state to False
        :param task: Task object
        :return: Task object
        """
        assert isinstance(task, Task)
        if task is not None:
            task.deleted = False
            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def complete(self, task: Task) -> Task:
        """
        Changes the completed state to True
        :param task: Task object
        :return: Task object
        """
        assert isinstance(task, Task)
        if task is not None:
            task.completed = True
            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def reset(self, task: Task) -> Task:
        """
        Resets the due date to today on the selected task
        :param task: Task object
        :return: Task object
        """
        assert isinstance(task, Task)
        if task is not None:
            today = Today()
            task.completed = False
            task.due_date = today.to_date_string()
            task.due_date_timestamp = today.to_timestamp()
            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def replace(self, local_task: Task, remote_task: Task, save: bool = True) -> Task:
        assert isinstance(remote_task, Task)
        assert isinstance(local_task, Task)

        remote_task.index = local_task.index
        remote_task.unique_id = local_task.unique_id
        remote_task.due_date = local_task.due_date
        remote_task.due_date_timestamp = local_task.due_date_timestamp

        if save:
            self.__db.replace_object(remote_task, local_task.index)
            self.logger.debug(f"Replaced local_task: {dict(local_task)} with remote_task: {dict(remote_task)}")
        return remote_task

    def insert(self, task: Task, save: bool = True) -> Task:
        assert isinstance(task, Task)
        if save:
            return self.__db.append_object(task)
        return task

    def update_all(self, task_list: List[Task]) -> List[Task]:
        return self.__db.update_objects(task_list)

    def edit(self, index: int,
             name: str = None,
             label: str = None,
             project: str = None,
             date_expression: str = None,
             time_spent: int = None) -> Task:

        task = self.get_task_by_index(index)
        if task is not None:
            task.name = name
            task.project = project
            task.label = label
            task.time_spent = time_spent

            if date_expression is not None:
                if self.__date_generator.validate_input(date_expression):
                    due_date = self.__date_generator.get_due_date(date_expression)
                    task.due_date = due_date.date_string
                    task.due_date_timestamp = due_date.to_timestamp()
                else:
                    self.logger.info(f"Provided due date {date_expression} is invalid")

            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def reschedule(self) -> None:
        today = Today()
        for task in self.get_task_list():
            if self.__calendar.is_past(DueDate(task.due_date), today) and task.completed is False and task.deleted is False:
                task.due_date = today.to_date_string()
                task.due_date_timestamp = today.to_timestamp()
                self.__db.replace_object(task)

    def get_list_by_type(self, parameter_name: str, value: str, task_list=None) -> list:
        """
        Returns list of tasks when a task parameter (ie. project, name, label) matches
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

    def get_label_list(self) -> List[str]:
        return self.unique("label", self.get_task_list())

    def get_project_list(self) -> List[str]:
        return self.unique("project", self.get_task_list())

    def get_due_date_list(self) -> List[str]:
        return list(set([task.due_date.date_string for task in self.get_task_list()]))

    @staticmethod
    def unique(parameter_name: str, task_list: list) -> List[str]:
        assert type(parameter_name) is str
        assert type(task_list) is list
        unique_set = set([getattr(task, parameter_name) for task in task_list])
        unique_set.discard("")
        return sorted(list(unique_set))

    def clear(self):
        self.__db.clear()
