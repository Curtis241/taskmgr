from datetime import datetime

import requests
from google.auth.exceptions import DefaultCredentialsError

from googleapiclient.discovery import build

from taskmgr.lib.google_auth import GoogleAuth
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class GTaskList:
    """
    Models the structure of Google Tasks service tasklist object. Detailed description found here:
    https://developers.google.com/tasks/v1/reference/tasks

    Creating an object allows the tasklist structure model to be serialized from the Google Tasks service
    to an object and then converted to a dictionary when __iter__ is called by using dict(object) method.
    """

    def __init__(self):
        self.__kind = "tasks#taskList"
        self.__id = str()
        self.__title = str()

        dt = datetime.now()
        self.__updated = dt.strftime(CommonVariables.rfc3339_date_time_format)
        self.__tasks = list()

    @property
    def kind(self):
        return self.__kind

    @kind.setter
    def kind(self, kind):
        self.__kind = kind

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def tasks(self):
        return self.__tasks

    def append(self, task):
        assert type(task) is GTask
        self.__tasks.append(task)

    def __iter__(self):
        yield 'kind', self.__kind
        yield 'id', self.__id
        yield 'title', self.__title


class GTask:
    """
    Models the structure of Google Tasks service task object. Detailed description found here:
    https://developers.google.com/tasks/v1/reference/tasks

    Creating an object allows the task structure model to be serialized from the Google Tasks service
    to an object and then converted to a dictionary when __iter__ is called by using dict(object) method.
    """

    def __init__(self):
        self.__kind = "tasks#task"
        self.__id = str()
        self.__title = str()
        self.__parent = str(0)
        self.__position = str(0)
        self.__notes = str()
        self.__status = 'needsAction'
        self.__updated = self.get_current_date()
        self.__due = str()
        self.__is_completed = False
        self.__completed = str()
        self.__deleted = False
        self.__hidden = False

    def __iter__(self):
        yield 'kind', self.__kind
        yield 'id', self.__id
        yield 'title', self.__title
        yield 'parent', self.__parent
        # yield 'position', self.__position
        yield 'notes', self.__notes
        yield 'status', self.__status
        # yield 'updated', self.__updated

        # if due and completed are included when they are empty
        # service throws 404 error.
        if len(self.__due) > 0:
            yield 'due', self.__due

        if len(self.__completed) > 0:
            yield 'completed', self.__completed

        yield 'deleted', self.__deleted
        yield 'hidden', self.__hidden

    @staticmethod
    def get_current_date():
        dt = datetime.now()
        return dt.strftime(CommonVariables.rfc3339_date_time_format)

    def is_completed(self, completed):
        assert type(completed) is bool
        if completed:
            self.__status = "completed"
            self.__completed = self.get_current_date()

    @property
    def kind(self):
        return self.__kind

    @kind.setter
    def kind(self, kind):
        self.__kind = kind

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, notes):
        self.__notes = notes

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def updated(self):
        return self.__updated

    @updated.setter
    def updated(self, updated):
        self.__updated = updated

    @property
    def due(self):
        return self.__due

    @due.setter
    def due(self, due):
        self.__due = due

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, completed):
        self.__completed = completed

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, deleted):
        self.__deleted = deleted

    @property
    def hidden(self):
        return self.__hidden

    @hidden.setter
    def hidden(self, hidden):
        self.__hidden = hidden


class GoogleTasksService:
    """
    Connects to the Google Tasks service using OAuth 2.0 authorization. For general info:
    https://en.wikipedia.org/wiki/OAuth.
    Steps:
    1. Create a credentials.json file that contains the project and the auth_uri. If the file
    does not exist it can be generated using the https://console.developers.google.com/apis/dashboard
    2. Save the file to the ~/.config/taskmgr/credentials/ directory.
    3. If the token.pickle file exists then the connection to the Google Tasks service is complete. If
    it does not exist then the Google Tasks service will begin the authentication process by displaying
    the login prompt and requesting authorization for the application.
    """
    logger = AppLogger("google_tasks_service").get_logger()

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/tasks']

    def __init__(self):
        self.service = None
        self.credentials = GoogleAuth.get_credentials(GoogleTasksService.SCOPES)
        self.empty_tasklist = {'kind': 'tasks#taskLists', 'items': []}
        self.empty_tasks = {'kind': 'tasks#tasks', 'items': []}
        try:
            self.logger.info(f"Connecting to google tasks api")
            self.logger.info(f"Completed retrieving credentials")
            self.service = build('tasks', 'v1', credentials=self.credentials)
            self.logger.info(f"Completed building resource")

        except DefaultCredentialsError as ex:
            GoogleTasksService.logger.info(ex)

    def list_tasklist(self) -> dict:
        if self.service is not None:
            return self.service.tasklists().list(maxResults=100).execute()
        else:
            return self.empty_tasklist

    def get_tasklist(self, tasklist_id) -> dict:
        if self.service is not None:
            return self.service.tasklists().get(tasklist=tasklist_id).execute()
        else:
            return self.empty_tasklist

    def insert_tasklist(self, tasklist_title) -> dict:
        if self.service is not None:
            return self.service.tasklists().insert(body={"title": tasklist_title}).execute()
        else:
            return self.empty_tasklist

    def delete_tasklist(self, tasklist_id) -> bool:
        if self.service is not None:
            self.service.tasklists().delete(tasklist=tasklist_id).execute()
            return True
        else:
            return False

    def update_tasklist(self, tasklist_id, tasklist) -> dict:
        if self.service is not None:
            return self.service.tasklists().update(tasklist=tasklist_id, body=tasklist).execute()
        else:
            return self.empty_tasklist

    def list_tasks(self, tasklist_id) -> dict:
        assert type(tasklist_id) is str and len(tasklist_id) > 0
        if self.credentials is not None:
            try:
                header_dict = {"Authorization": f"Bearer {self.credentials.token}"}
                params_dict = {"showDeleted": True, "showCompleted": True, "showHidden": True, "maxResults": 100}
                response = requests.get(f"https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks",
                                        params=params_dict,
                                        headers=header_dict)
                return response.json()
            except BaseException as ex:
                self.logger.error(ex)
        else:
            return self.empty_tasks

    def insert_task(self, tasklist_id, task) -> None:
        if self.service is not None:
            return self.service.tasks().insert(tasklist=tasklist_id, body=task).execute()

    def clear_tasks(self, tasklist_id) -> None:
        if self.service is not None:
            return self.service.tasks().clear(tasklist=tasklist_id).execute()

    def delete_task(self, tasklist_id, task_id) -> None:
        if self.service is not None:
            return self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()

    def update_task(self, tasklist_id, task_id, task) -> None:
        if self.service is not None:
            self.service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()


class TasksListAPI:
    logger = AppLogger("tasks_list_api").get_logger()

    def __init__(self, tasks_service):
        self.service = tasks_service

    @staticmethod
    def to_object(tasklist_dict):
        if type(tasklist_dict) is dict:
            obj = GTaskList()
            for key, value in tasklist_dict.items():
                setattr(obj, key, value)
            return obj
        else:
            return tasklist_dict

    @staticmethod
    def to_object_list(tasklist_list):
        assert type(tasklist_list) is list
        return [TasksListAPI.to_object(tasklist_dict) for tasklist_dict in tasklist_list]

    def list(self) -> list:
        results = self.service.list_tasklist()
        tasklist_list = results.get('items', [])
        if not tasklist_list:
            self.logger.error('No tasklists found.')
        return self.to_object_list(tasklist_list)

    def get(self, title):
        assert type(title) is str and len(title) > 0
        tasklist_list = self.to_object_list([tasklist for tasklist in self.list() if tasklist.title == title])
        if len(tasklist_list) > 0:
            return tasklist_list[0]

    def insert(self, title):
        assert type(title) is str and len(title) > 0
        if self.get(title) is None:
            tasklist_dict = self.service.insert_tasklist(title)
            return self.to_object(tasklist_dict)
        else:
            self.logger.error(f"{title} already exists")

    def delete(self, title):
        assert type(title) is str and len(title) > 0
        tasklist = self.get(title)
        if tasklist is not None:
            self.service.delete_tasklist(tasklist.id)
            return True
        else:
            self.logger.error("{} does not exist".format(title))

    def update(self, current_title, new_title):
        assert type(current_title) is str and len(current_title) > 0
        assert type(new_title) is str and len(new_title) > 0

        tasklist = self.get(current_title)
        if tasklist is not None:
            tasklist.title = new_title
            tasklist_dict = self.service.update_tasklist(tasklist.id, dict(tasklist))
            return self.to_object(tasklist_dict)


class TasksAPI:
    logger = AppLogger("tasks_api").get_logger()

    def __init__(self, tasklist_id, tasks_service):
        assert type(tasklist_id) is str
        self.service = tasks_service
        self.tasklist_id = tasklist_id

    @staticmethod
    def to_object(task_dict):

        if type(task_dict) is dict:
            obj = GTask()
            for key, value in task_dict.items():
                setattr(obj, key, value)
            return obj
        else:
            return task_dict

    @staticmethod
    def to_object_list(task_list):
        assert type(task_list) is list
        return [TasksAPI.to_object(task_dict) for task_dict in task_list]

    def list(self):
        results = self.service.list_tasks(self.tasklist_id)
        task_items = results.get('items', [])
        return self.to_object_list(task_items)

    def get(self, title):
        assert type(title) is str and len(title) > 0
        for task in self.list():
            if task.title == title:
                return task

    def insert(self, task_obj) -> bool:
        assert type(task_obj) is GTask
        assert len(task_obj.title) > 0

        if self.service is None:
            return False

        if self.get(task_obj.title) is None:
            self.service.insert_task(self.tasklist_id, dict(task_obj))
            return True
        else:
            self.logger.debug("{} already exists".format(task_obj.title))
            return False

    def clear(self):
        self.service.clear_tasks(self.tasklist_id)

    def delete(self, title) -> bool:
        task = self.get(title)
        if task is not None:
            self.service.delete_task(self.tasklist_id, task.id)
            return True
        return False

    def update(self, task_obj):
        assert type(task_obj) is GTask
        assert len(task_obj.title) > 0

        task = self.get(task_obj.title)
        if task is not None:
            task_obj.id = task.id
            return self.to_object(self.service.update_task(self.tasklist_id, task.id, dict(task_obj)))
