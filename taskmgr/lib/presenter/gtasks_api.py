from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.gtask import GTask


class GTasksAPI:
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
        return [GTasksAPI.to_object(task_dict) for task_dict in task_list]

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
