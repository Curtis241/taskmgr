from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.gtask_list import GTaskList


class GTasksListAPI:
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
        return [GTasksListAPI.to_object(tasklist_dict) for tasklist_dict in tasklist_list]

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