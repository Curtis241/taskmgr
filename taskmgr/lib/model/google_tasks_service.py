import requests
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.google_auth import GoogleAuth


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

    def __init__(self):
        self.service = None
        self.credentials = GoogleAuth().get_credentials()
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