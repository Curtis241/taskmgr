from google.auth.exceptions import DefaultCredentialsError
from google.cloud import datastore

from taskmgr.lib.model.google_auth import GoogleAuth
from taskmgr.lib.logger import AppLogger


class GoogleDatastoreService:
    """
    Generic class used to send json object to google datastore.
    """
    logger = AppLogger("google_datastore_service").get_logger()

    def __init__(self):
        pass

    @staticmethod
    def get_client():
        try:
            google_auth = GoogleAuth()
            credentials = google_auth.get_credentials()
            project_name = google_auth.get_project_name()
            GoogleDatastoreService.logger.debug("Retrieved datastore credentials {}".format(credentials))
            return datastore.Client(project=project_name, credentials=credentials)

        except DefaultCredentialsError as ex:
            GoogleDatastoreService.logger.info(ex)

    @staticmethod
    def get_last_entity(entity_kind):
        assert type(entity_kind) is str
        client = GoogleDatastoreService.get_client()
        query = client.query()
        query.keys_only()
        entity_list = [entity for entity in list(query.fetch()) if entity.kind == entity_kind]
        if len(entity_list) > 0:
            return entity_list[-1].id + 1
        else:
            return 1

    @staticmethod
    def save(last_entity_id, entity_list):
        assert type(last_entity_id) is int
        assert type(entity_list) is list

        client = GoogleDatastoreService.get_client()
        for entity_id, entity_obj in enumerate(entity_list, start=last_entity_id):
            key = client.key(entity_obj.entity_name, entity_id)
            entity = datastore.Entity(key=key)
            entity.update(dict(entity_obj))
            client.put(entity)
            result = client.get(key)
            GoogleDatastoreService.logger.info(result)
