import os
import os.path
import pickle

import dpath
import ujson
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class GoogleAuth:
    """
    Manages the Google Oauth and service credentials for the Tasks
    and Datastore services in the .config/taskmgr/credentials directory.
    """
    logger = AppLogger("google_auth").get_logger()

    def __init__(self):
        self.credentials_dir = CommonVariables().credentials_dir
        os.makedirs(self.credentials_dir, 0o777, exist_ok=True)
        self.credentials_path = f'{self.credentials_dir}credentials.json'

    def get_project_name(self):
        if os.path.exists(self.credentials_path):
            with open(self.credentials_path, 'r') as infile:
                json = ujson.load(infile)
                return dpath.get(json, "/installed/project_id")

    def get_credentials(self):
        """
        Manages the authentication process for connecting to the Google Tasks service. The file token.pickle
        stores the user's access and refresh tokens, and is created automatically when the authorization
        flow completes for the first time.
        """
        creds = None

        token_path = f'{self.credentials_dir}token.pickle'
        scopes = ["https://www.googleapis.com/auth/tasks",
                  "https://www.googleapis.com/auth/datastore"]

        if os.path.exists(self.credentials_path):
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, scopes)
                    creds = flow.run_local_server()
                # Save the credentials for the next run
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        else:
            GoogleAuth.logger.info("~/.config/taskmgr/credentials/credentials.json does not exist")

        return creds

