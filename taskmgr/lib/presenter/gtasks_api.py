from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.gtask import GTask


class GTasksAPI:
    logger = AppLogger("gtasks_api").get_logger()

    def __init__(self, tasklist_id, tasks_service):
        assert type(tasklist_id) is str
        self.service = tasks_service
        self.tasklist_id = tasklist_id

    @staticmethod
    def to_object(gtask_dict):

        if type(gtask_dict) is dict:
            obj = GTask()
            for key, value in gtask_dict.items():
                setattr(obj, key, value)
            return obj
        else:
            return gtask_dict

    @staticmethod
    def to_object_list(gtask_list):
        assert type(gtask_list) is list
        return [GTasksAPI.to_object(gtask_dict) for gtask_dict in gtask_list]

    def list(self):
        results = self.service.list_tasks(self.tasklist_id)
        task_items = results.get('items', [])
        return self.to_object_list(task_items)

    def get_by_id(self, gtask_id):
        assert type(gtask_id) is str and len(gtask_id) > 0
        for task in self.list():
            if task.id == gtask_id:
                return task

    def get_by_title(self, title):
        assert type(title) is str and len(title) > 0
        for task in self.list():
            if task.title == title:
                return task

    def insert(self, task_obj) -> GTask:
        assert type(task_obj) is GTask
        assert len(task_obj.title) > 0

        if self.service is not None:
            gtask_dict = self.service.insert_task(self.tasklist_id, dict(task_obj))
            return self.to_object(gtask_dict)

    def clear(self):
        self.service.clear_tasks(self.tasklist_id)

    def delete(self, title) -> bool:
        task = self.get_by_title(title)
        if task is not None:
            self.service.delete_task(self.tasklist_id, task.id)
            return True
        return False

    def update(self, gtask) -> GTask:
        assert type(gtask) is GTask
        assert len(gtask.id) > 0

        return self.to_object(self.service.update_task(self.tasklist_id, gtask.id, dict(gtask)))
