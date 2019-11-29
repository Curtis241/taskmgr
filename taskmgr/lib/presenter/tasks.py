import uuid
from copy import deepcopy

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
    Complete = 'complete'
    Incomplete = "incomplete"
    Label = "label"
    Project = "project"
    DueDate = "due_date"
    Text = "text"

    @staticmethod
    def contains(value):
        return value in SortType.__dict__.values()


class Tasks(Model):
    """
    Main entry point for querying and managing local tasks.
    """
    logger = AppLogger("tasks").get_logger()

    def __init__(self, file_database):
        super().__init__(file_database)
        self.__calendar = Calendar()

    def add(self, obj):
        assert type(obj) is Task
        obj.id = uuid.uuid4().hex
        obj.index = self.get_index()
        obj.last_updated = self.get_date_time_string()
        self.append(obj)
        self.logger.debug(f"Added {dict(obj)}")
        self.save()
        return obj

    def get_task(self, func) -> Task:
        for task in self.get_list():
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
        return self.get_task(lambda task: task if task.id == task_id else None)

    def get_task_by_name(self, task_name) -> Task:
        assert type(task_name) is str
        return self.get_task(lambda task: task if task.text == task_name else None)

    def get_list_by_type(self, sort_type, value, include_deleted=False):
        assert SortType.contains(sort_type)
        assert type(value) == str

        if include_deleted:
            task_list = self.get_list()
        else:
            task_list = self.get_filtered_list()

        return list(filter(lambda t: getattr(t, sort_type) == value, task_list))

    def get_filtered_list(self):
        return [task for task in self.get_list() if not task.deleted]

    def delete(self, task_id) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.last_updated = self.get_date_time_string()
            task.deleted = True
            self.insert(task.index, task)
            self.logger.debug(f"Deleted {dict(task)}")
            self.save()
            return task
        else:
            raise TaskKeyError()

    def complete(self, task_id) -> Task:
        assert type(task_id) is str

        task = self.get_task_by_id(task_id)
        if task is not None:
            task.last_updated = self.get_date_time_string()
            task.complete()
            self.insert(task.index, task)
            self.save()
            return task
        else:
            raise TaskKeyError()

    def reset(self, task_id) -> Task:
        """
        Resets the due date on the selected task to today
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
            self.insert(task.index, task)
            self.save()
            return task
        else:
            raise TaskKeyError()

    def replace(self, local_task, remote_task) -> Task:
        assert type(remote_task) is Task
        assert type(local_task) is Task

        if local_task is not None:
            remote_task.last_updated = self.get_date_time_string()
            remote_task.index = local_task.index
            self.insert(local_task.index, remote_task)
            self.save()
            self.logger.debug(f"Replaced local_task: {dict(local_task)} with remote_task: {dict(remote_task)}")
            return remote_task

    def edit(self, task_id, text, label, project, date_expression) -> Task:
        task = deepcopy(self.get_task_by_id(task_id))
        if task is not None:
            task.text = text
            task.label = label
            task.project = project
            task.date_expression = date_expression
            task.last_updated = self.get_date_time_string()
            self.insert(task.index, task)
            self.save()
            return task
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

    def sort(self, sort_type):
        assert SortType.contains(sort_type)
        return [t for t in sorted(self.get_list(), key=lambda t: getattr(t, sort_type))]

    def unique(self, sort_type, include_deleted=False):
        assert SortType.contains(sort_type)

        if include_deleted:
            task_list = self.get_list()
        else:
            task_list = self.get_filtered_list()

        return set([getattr(t, sort_type) for t in task_list])

    def from_dict(self, dict_list):
        assert type(dict_list) is list

        for index, obj_dict in enumerate(dict_list):
            task = Task(getattr(obj_dict, "text", str()))
            task.index = index
            for key, value in obj_dict.items():
                if type(value) is list:
                    task.due_dates = [DueDate().from_dict(due_date_dict) for due_date_dict in value]
                else:
                    setattr(task, key, value)
            self.append(task)
        return self.get_list()
