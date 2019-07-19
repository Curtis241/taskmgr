import os.path
import pathlib
import pickle
from abc import ABC, abstractmethod
from datetime import datetime

import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class GTaskList:

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
        yield 'position', self.__position
        yield 'notes', self.__notes
        yield 'status', self.__status
        yield 'updated', self.__updated

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


class TasksService(ABC):

    @abstractmethod
    def list_tasklist(self): pass

    @abstractmethod
    def get_tasklist(self, tasklist_id): pass

    @abstractmethod
    def insert_tasklist(self, tasklist_title): pass

    @abstractmethod
    def delete_tasklist(self, tasklist_id): pass

    @abstractmethod
    def update_tasklist(self, tasklist_id, tasklist): pass

    @abstractmethod
    def list_tasks(self, tasklist_id): pass

    @abstractmethod
    def insert_task(self, tasklist_id, task): pass

    @abstractmethod
    def clear_tasks(self, tasklist_id): pass

    @abstractmethod
    def delete_task(self, tasklist_id, task_id): pass

    @abstractmethod
    def update_task(self, tasklist_id, task_id, task): pass


class GoogleTasksService(TasksService):
    logger = AppLogger("google_tasks_service").get_logger()

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/tasks']

    def __init__(self):
        start_datetime = datetime.now()
        self.logger.info(f"Connecting to google tasks api")
        creds = self.get_credentials()
        self.logger.info(f"Completed retrieving credentials")
        self.service = self.build_resource(creds)

        end_datetime = datetime.now()
        duration = (end_datetime - start_datetime).total_seconds()
        self.logger.info(
            f"Completed building resource: (Duration: {duration})")

    @staticmethod
    def get_credentials():
        """Shows basic usage of the Tasks API.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        credentials_dir = GoogleTasksService.get_dir()
        pickle_path = f'{credentials_dir}/token.pickle'
        credentials_path = f"{credentials_dir}/credentials.json"

        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, GoogleTasksService.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(pickle_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    @staticmethod
    def get_dir():
        credentials_dir = CommonVariables.credentials_dir
        os.makedirs(f"{credentials_dir}", 0o777, exist_ok=True)
        return credentials_dir

    @staticmethod
    def build_resource(creds):
        return build('tasks', 'v1', credentials=creds)

    def list_tasklist(self):
        return self.service.tasklists().list(maxResults=100).execute()

    def get_tasklist(self, tasklist_id):
        return self.service.tasklists().get(tasklist=tasklist_id).execute()

    def insert_tasklist(self, tasklist_title):
        return self.service.tasklists().insert(body={"title": tasklist_title}).execute()

    def delete_tasklist(self, tasklist_id):
        return self.service.tasklists().delete(tasklist=tasklist_id).execute()

    def update_tasklist(self, tasklist_id, tasklist):
        return self.service.tasklists().update(tasklist=tasklist_id, body=tasklist).execute()

    def list_tasks(self, tasklist_id):
        assert type(tasklist_id) is str and len(tasklist_id) > 0
        creds = self.get_credentials()
        try:
            header_dict = {"Authorization": f"Bearer {creds.token}"}
            params_dict = {"showDeleted": True, "showCompleted": True, "showHidden": True}
            response = requests.get(f"https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks",
                                    params=params_dict,
                                    headers=header_dict)
            return response.json()
        except BaseException as ex:
            self.logger.error(ex)

    def insert_task(self, tasklist_id, task):
        return self.service.tasks().insert(tasklist=tasklist_id, body=task).execute()

    def clear_tasks(self, tasklist_id):
        return self.service.tasks().clear(tasklist=tasklist_id).execute()

    def delete_task(self, tasklist_id, task_id):
        return self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()

    def update_task(self, tasklist_id, task_id, task):
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

    def list(self):
        results = self.service.list_tasklist()
        tasklist_list = results.get('items', [])
        if not tasklist_list:
            self.logger.info('No tasklists found.')
        return self.to_object_list(tasklist_list)

    def get(self, title):
        assert type(title) is str and len(title) > 0
        tasklist_list = self.to_object_list([tasklist for tasklist in self.list() if tasklist.title == title])
        if len(tasklist_list) > 0:
            return tasklist_list[0]
        else:
            return None

    def insert(self, title):
        assert type(title) is str and len(title) > 0
        if self.get(title) is None:
            self.logger.info(f"Beginning tasklist insert: {datetime.now()}")
            tasklist_dict = self.service.insert_tasklist(title)
            self.logger.info(f"Inserted {title} tasklist: {datetime.now()}")
            return self.to_object(tasklist_dict)
        else:
            self.logger.error(f"{title} already exists")

    def delete(self, title):
        assert type(title) is str and len(title) > 0
        tasklist = self.get(title)
        if tasklist is not None:
            self.service.delete_tasklist(tasklist.id)
            self.logger.debug(f"Deleted {title} tasklist")
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
            self.logger.info("Updated {} to {}".format(current_title, new_title))
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
            TasksAPI.logger.debug(f"TasksAPI.to_object: {task_dict}")
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

    def insert(self, task_obj):
        assert type(task_obj) is GTask
        assert len(task_obj.title) > 0

        if self.get(task_obj.title) is None:
            self.logger.info("Inserted {}".format(task_obj.title))
            self.service.insert_task(self.tasklist_id, dict(task_obj))
            return True
        else:
            self.logger.info("{} already exists".format(task_obj.title))

    def clear(self):
        self.logger.info("Cleared {} tasklist".format(self.tasklist_id))
        self.service.clear_tasks(self.tasklist_id)

    def delete(self, title):
        task = self.get(title)
        if task is not None:
            self.service.delete_task(self.tasklist_id, task.id)
            self.logger.info("Deleted {}".format(task.title))
            return True

    def update(self, task_obj):
        assert type(task_obj) is GTask
        assert len(task_obj.title) > 0

        task = self.get(task_obj.title)
        if task is not None:
            self.logger.info("Updated {}".format(task.title))
            task_obj.id = task.id
            return self.to_object(self.service.update_task(self.tasklist_id, task.id, dict(task_obj)))
