from typing import Set

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.model import Model
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_generator import Calendar, Day, DueDate, Today


class TaskKeyError(IndexError):
    logger = AppLogger("task_key_error").get_logger()
    msg = "task.key cannot be found"

    def __init__(self):
        super().__init__(self.msg)
        self.logger.error(self.msg)


class SortType:
    Status = "status"
    Label = "label"
    Project = "project"
    DueDate = "due_date"
    DueDateRange = "due_date_range"
    Text = "text"

    @staticmethod
    def contains(value):
        return value in SortType.__dict__.values()


class Tasks(Model):
    """
    Main entry point for querying and managing local tasks.
    """
    logger = AppLogger("tasks").get_logger()

    def __init__(self, database):
        super().__init__(database, Task())
        self.__calendar = Calendar()

    def add(self, obj):
        assert type(obj) is Task
        return self.append_object(obj)

    def get_task(self, func) -> Task:
        for task in self.get_object_list():
            if func(task) is not None:
                self.logger.debug(f"Retrieved task by index: {task.index}, text: {task.text}")
                return task

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

    def get_list_by_type(self, sort_type, value, include_deleted=False):
        assert SortType.contains(sort_type)
        assert type(value) == str

        if include_deleted:
            task_list = self.get_object_list()
        else:
            task_list = self.get_filtered_list()

        return list(filter(lambda t: getattr(t, sort_type) == value, task_list))

    def get_filtered_list(self):
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

    def sort(self, sort_type):
        assert SortType.contains(sort_type)
        return [t for t in sorted(self.get_object_list(), key=lambda t: getattr(t, sort_type))]

    def unique(self, sort_type, include_deleted=False) -> Set[Task]:
        assert SortType.contains(sort_type)

        if include_deleted:
            task_list = self.get_object_list()
        else:
            task_list = self.get_filtered_list()

        return set([getattr(t, sort_type) for t in task_list])

    def clear(self):
        self.clear_objects()
