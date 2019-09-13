from google.auth.exceptions import DefaultCredentialsError
from google.cloud import datastore

from taskmgr.lib.google_auth import GoogleAuth
from taskmgr.lib.logger import AppLogger


class GoogleDatastoreService:

    logger = AppLogger("google_datastore_service").get_logger()
    SCOPES = ["https://www.googleapis.com/auth/datastore"]

    def __init__(self):
        try:
            credentials = GoogleAuth().get_credentials(GoogleDatastoreService.SCOPES)
            self.client = datastore.Client(credentials=credentials)

            key = self.client.key('EntityKind', 1234)
            entity = datastore.Entity(key=key)
            entity.update({
                'foo': u'bar',
                'baz': 1337,
                'qux': False,
            })
            self.client.put(entity)
            result = self.client.get(key)
            print(result)
        except DefaultCredentialsError as ex:
            GoogleDatastoreService.logger.info(ex)
