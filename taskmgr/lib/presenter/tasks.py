from copy import deepcopy
from typing import List, Optional, Tuple

from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.database.tasks_db import TasksDatabase
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.calendar import Calendar, Today
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.date_time_generator import DateTimeGenerator
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

    def __init__(self, database: TasksDatabase):
        assert isinstance(database, TasksDatabase)

        self.__db = database
        self.__calendar = Calendar()
        self.__vars = CommonVariables()
        self.__date_generator = DateTimeGenerator()

    def add(self, name: str, label: str, project: str, date_expression: str) -> List[Task]:

        if not date_expression:
            raise DueDateError(f"Provided due date {date_expression} is empty")

        task_list = list()
        if self.__date_generator.validate_input(date_expression):
            for day in self.__date_generator.get_days(date_expression):
                task = Task(name)
                task.label = label
                task.project = project
                task.due_date = day.to_date_string()
                task.due_date_timestamp = day.to_date_timestamp()
                task.completed = False
                self.__db.append_object(task)
                task_list.append(task)
        else:
            raise DueDateError(f"Provided due date {date_expression} is invalid")

        return task_list

    def get_all(self, page: int = 0) -> QueryResult:
        self.__db.set_page_number(page)
        return self.__db.get_all()

    def get_tasks_containing_name(self, value: str, page: int = 0) -> QueryResult:
        assert type(value) is str
        self.__db.set_page_number(page)
        return self.__db.get_selected("name", str(value).lower())

    def get_task_by_index(self, index: int) -> Task:
        assert type(index) is int
        return self.__db.get_object("index", index)

    def get_task_by_id(self, task_id: str) -> Task:
        assert type(task_id) is str
        return self.__db.get_object("unique_id", task_id)

    def get_task_by_name(self, task_name: str) -> Task:
        assert type(task_name) is str
        return self.__db.get_object("name", task_name)

    def get_tasks_by_date(self, date_expression: str) -> QueryResult:
        assert type(date_expression) is str
        result = QueryResult()
        days = self.__date_generator.get_days(date_expression)
        for day in days:
            selection = self.__db.get_selected("due_date_timestamp", day.to_date_timestamp())
            result.extend(selection.to_list())
        return result

    def get_tasks_within_date_range(self, min_date: str, max_date: str, page: int) -> QueryResult:
        assert type(min_date) is str
        assert type(max_date) is str

        min_day = self.__date_generator.get_day(min_date)
        max_day = self.__date_generator.get_day(max_date)

        self.__db.set_page_number(page)
        return self.__db.get_selected("due_date_timestamp",
                                      min_day.to_date_timestamp(),
                                      max_day.to_date_timestamp())

    def get_tasks_by_status(self, is_completed: bool, page: int) -> QueryResult:
        assert type(is_completed) is bool
        self.__db.set_page_number(page)
        if is_completed:
            return self.__db.get_selected("completed", "True")
        else:
            return self.__db.get_selected("completed", "False")

    def get_tasks_by_project(self, project: str, page: int = 0) -> QueryResult:
        assert type(project) is str
        self.__db.set_page_number(page)
        return self.__db.get_selected("project", project)

    def get_tasks_by_label(self, label: str, page: int = 0) -> QueryResult:
        assert type(label) is str
        self.__db.set_page_number(page)
        return self.__db.get_selected("label", label)

    def get_undeleted_tasks(self, page: int = 0) -> QueryResult:
        self.__db.set_page_number(page)
        return self.__db.get_selected("deleted", "False")

    def delete(self, task: Task, save: bool = True) -> Optional[Task]:
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

    def undelete(self, task: Task) -> Optional[Task]:
        """
        Changes the deleted state to False
        """
        assert isinstance(task, Task)
        if task is not None:
            task.deleted = False
            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def complete(self, task: Task) -> Optional[Task]:
        """
        Changes the completed state to True
        """
        assert isinstance(task, Task)
        if task is not None:
            task.completed = True
            return self.__db.replace_object(task)
        else:
            raise TaskKeyError()

    def incomplete(self, task: Task) -> Optional[Task]:
        """
        Changes the completed status to False
        """
        assert isinstance(task, Task)
        if task is not None:
            task.completed = False
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
        return self.__db.append_objects(task_list)

    def edit(self, index: int,
             name: str = None,
             label: str = None,
             project: str = None,
             date_expression: str = None,
             time_spent: int = None) -> Optional[Tuple[Task, Task]]:

        original_task = self.get_task_by_index(index)
        if original_task is not None:
            new_task = deepcopy(original_task)
            new_task.name = name
            new_task.project = project
            new_task.label = label
            new_task.time_spent = time_spent

            if date_expression is not None:
                if self.__date_generator.validate_input(date_expression):
                    day = self.__date_generator.get_day(date_expression)
                    new_task.due_date = day.to_date_string()
                    new_task.due_date_timestamp = day.to_date_timestamp()
                else:
                    self.logger.info(f"Provided due date {date_expression} is invalid")

            return original_task, self.__db.replace_object(new_task)
        else:
            raise TaskKeyError()

    def reschedule(self) -> List[Task]:
        """
        Updates the date in tasks that are incomplete to today's date
        """
        today = Today()
        task_list = list()
        for task in self.__db.get_selected("completed", "False").to_list():
            selected_day = self.__date_generator.get_day(task.due_date)
            if self.__calendar.is_past(selected_day, today) and task.deleted is False:
                task.due_date = today.to_date_string()
                task.due_date_timestamp = today.to_date_timestamp()
                task_list.append(task)

        return task_list

    def get_label_list(self) -> List[str]:
        return sorted(self.__db.unique("label"))

    def get_project_list(self) -> List[str]:
        return sorted(self.__db.unique("project"))

    def get_due_date_list(self) -> List[str]:
        return sorted(self.__db.unique("due_date"))

    def clear(self):
        self.__db.clear()
