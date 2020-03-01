from datetime import datetime
from typing import Set, List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import Calendar, Day, DueDate, Today
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
        self.vars = CommonVariables()

    def add(self, obj):
        assert type(obj) is Task
        return self.append_object(obj)

    def contains_due_date_range(self, task, min_date_string, max_date_string):
        for due_date in task.due_dates:
            min_day = Day(datetime.strptime(min_date_string, self.vars.date_format))
            max_day = Day(datetime.strptime(max_date_string, self.vars.date_format))
            if len(due_date.date_string) > 0:
                day = Day(datetime.strptime(due_date.date_string, self.vars.date_format))

                if min_day.to_date_time() < day.to_date_time() < max_day.to_date_time():
                    return task

    def get_task(self, func) -> Task:
        for task in self.get_object_list():
            if func(task) is not None:
                self.logger.debug(f"Retrieved task by index: {task.index}, text: {task.text}")
                return task

    def get_tasks_by_text(self, value) -> List[Task]:
        """
        Wrapped the get_list_by_type method because "text" is parameter in Task object
        :param value:
        :return: list of Task
        """
        assert type(value) is str
        return [task for task in self.get_filtered_list()
                if str(value).lower() in str(task.text).lower()]

    def get_task_by_index(self, index) -> Task:
        assert type(index) is int
        return self.get_task(lambda task: task if task.index == index else None)

    def get_task_by_external_id(self, external_id) -> Task:
        assert type(external_id) is str
        return self.get_task(lambda task: task if task.external_id == external_id else None)

    def get_task_by_id(self, task_id) -> Task:
        assert type(task_id) is str
        return self.get_task(lambda task: task if task.unique_id == task_id else None)

    def get_task_by_name(self, task_name) -> Task:
        assert type(task_name) is str
        return self.get_task(lambda task: task if task.text == task_name else None)

    def get_tasks_by_date(self, date_string) -> List[Task]:
        assert type(date_string) is str
        return [task for task in self.get_object_list() for due_date in task.due_dates
                if due_date.date_string == date_string]

    def get_tasks_within_date_range(self, min_date_string, max_date_string) -> List[Task]:
        assert type(min_date_string) is str
        assert type(max_date_string) is str
        return [task for task in self.get_object_list()
                if self.contains_due_date_range(task, min_date_string, max_date_string)]

    def get_tasks_by_status(self, is_completed) -> List[Task]:
        if is_completed:
            return [task for task in self.get_filtered_list() if task.is_completed()]
        else:
            return [task for task in self.get_filtered_list() if not task.is_completed()]

    def get_tasks_by_project(self, project, include_deleted) -> List[Task]:
        if include_deleted:
            task_list = self.get_object_list()
        else:
            task_list = self.get_filtered_list()
        return self.get_list_by_type("project", project, task_list)

    def get_tasks_by_label(self, label) -> List[Task]:
        task_list = self.get_filtered_list()
        return self.get_list_by_type("label", label, task_list)

    def get_filtered_list(self) -> List[Task]:
        return [task for task in self.get_object_list() if not task.deleted]

    def delete(self, task_id) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.deleted = True
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def complete(self, task_id) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.complete()
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def reset(self, task_id) -> Task:
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
            task.due_dates = [due_date]
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def replace(self, local_task, remote_task) -> Task:
        assert type(remote_task) is Task
        assert type(local_task) is Task

        if local_task is not None:
            remote_task.index = local_task.index
            self.replace_object(local_task.index, remote_task)
            self.logger.debug(f"Replaced local_task: {dict(local_task)} with remote_task: {dict(remote_task)}")
            return remote_task

    def edit(self, task_id, text, label, project, date_expression) -> Task:
        task = self.get_task_by_id(task_id)
        if task is not None:
            task.text = text
            task.label = label
            task.project = project
            task.date_expression = date_expression
            self.replace_object(task.index, task)
            return task
        else:
            raise TaskKeyError()

    def reschedule(self, today) -> None:
        assert type(today) is Today or Day
        task_list = self.get_object_list()
        for task in task_list:
            for due_date in task.due_dates:
                if self.__calendar.is_past(due_date, today) and due_date.completed is False:
                    due_date.date_string = today.to_date_string()
        self.update_objects(task_list)

    @staticmethod
    def get_list_by_type(parameter_name: str, value: str, task_list: list) -> list:
        """
        Returns list of tasks when a task parameter (ie. project, text, label) matches
        a single value.
        :param parameter_name:
        :param value:
        :param task_list:
        :return:
        """
        return list(filter(lambda t: getattr(t, parameter_name) == value, task_list))

    def __sort(self, parameter_name):
        assert type(parameter_name) is str
        return [t for t in sorted(self.get_object_list(), key=lambda t: getattr(t, parameter_name))]

    def get_label_set(self) -> Set[Task]:
        return self.unique("label", self.get_filtered_list())

    def get_project_set(self) -> Set[Task]:
        return self.unique("project", self.get_filtered_list())

    @staticmethod
    def unique(parameter_name, task_list) -> Set[Task]:
        assert type(parameter_name) is str
        assert type(task_list) is list
        return set([getattr(t, parameter_name) for t in task_list])

    def clear(self):
        self.clear_objects()
