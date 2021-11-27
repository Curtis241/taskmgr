from fastapi.exceptions import RequestValidationError

from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, task_list: list):
        return {"tasks": [dict(task) for task in task_list]}

    @staticmethod
    def display_attribute_error(attribute_name: str, message: str):
        return {"detail": [{"loc": ["param", attribute_name]}], "msg": message, "type": "attribute_error"}

    def display_snapshots(self, snapshots: Snapshots):
        return {"summary": snapshots.summarize(), "snapshots": [dict(snapshot) for snapshot in snapshots.get_list()]}

    def add_task(self, text: str, label: str, project: str, date_expression: str) -> dict:
        try:
            return self.display_tasks(self.tasks.add(text, label, project, date_expression))
        except AttributeError as ex:
            return ApiClient.display_attribute_error("date_expression", str(ex))

    def delete_task(self, unique_id: str) -> dict:
        result = self.tasks.delete(unique_id)
        return self.display_tasks([result])

    def complete_task(self, unique_id: str) -> dict:
        result = self.tasks.complete(unique_id)
        return self.display_tasks([result])

    def undelete_task(self, unique_id: str) -> dict:
        result = self.tasks.undelete(unique_id)
        return self.display_tasks([result])

    def reset_task(self, unique_id: str) -> dict:
        result = self.tasks.reset(unique_id)
        return self.display_tasks([result])

    def list_all_tasks(self) -> dict:
        task_list = self.tasks.get_object_list()
        return self.display_tasks(task_list)

