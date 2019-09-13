import os
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables


class GoogleAuth:
    logger = AppLogger("google_auth").get_logger()

    @staticmethod
    def get_credentials(scopes):
        """
        Manages the authentication process for connecting to the Google Tasks service.The file token.pickle
        stores the user's access and refresh tokens, and is created automatically when the authorization
        flow completes for the first time.
        """
        creds = None
        credentials_dir = GoogleAuth.get_dir()
        pickle_path = f'{credentials_dir}/token.pickle'
        credentials_path = f"{credentials_dir}/credentials.json"

        if os.path.exists(credentials_path):
            if os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, scopes)
                    creds = flow.run_local_server()
                # Save the credentials for the next run
                with open(pickle_path, 'wb') as token:
                    pickle.dump(creds, token)
        else:
            GoogleAuth.logger.info("~/.config/taskmgr/credentials.json does not exist")

        return creds

    @staticmethod
    def get_dir():
        credentials_dir = CommonVariables.credentials_dir
        os.makedirs(f"{credentials_dir}", 0o777, exist_ok=True)
        return credentials_dir
