from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, task_list: list):
        return {"tasks": [dict(task) for task in task_list]}

    def display_invalid_index_error(self, index: int):
        return {"detail": [{"loc": ["param", "index"]}], "msg": f"Provided index {index} is invalid",
                "type": "attribute_error"}

    def display_due_date_error(self, message: str):
        return {"detail": [{"loc": ["param", "due_date"]}], "msg": message, "type": "attribute_error"}

    def display_snapshots(self, snapshots: Snapshots, page: int):
        summary, snapshot_list = snapshots.get_snapshot()
        return {"snapshot": {"summary": summary.compose_summary(), "list": [dict(snapshot) for snapshot in snapshot_list]}}


    # def add_task(self, text: str, label: str, project: str, date_expression: str) -> dict:
    #     try:
    #         return self.display_tasks(self.tasks.add(text, label, project, date_expression))
    #     except AttributeError as ex:
    #         return ApiClient.display_attribute_error("date_expression", str(ex))

    # def delete_task(self, unique_id: str) -> dict:
    #     task = self.tasks.get_task_by_id(unique_id)
    #     result = self.tasks.delete(task)
    #     return self.display_tasks([result])
    #
    # def complete_task(self, unique_id: str) -> dict:
    #     task = self.tasks.get_task_by_id(unique_id)
    #     result = self.tasks.complete(task)
    #     return self.display_tasks([result])
    #
    # def undelete_task(self, unique_id: str) -> dict:
    #     task = self.tasks.get_task_by_id(unique_id)
    #     result = self.tasks.undelete(task)
    #     return self.display_tasks([result])
    #
    # def reset_task(self, unique_id: str) -> dict:
    #     task = self.tasks.get_task_by_id(unique_id)
    #     result = self.tasks.reset(task)
    #     return self.display_tasks([result])
    #
    # def list_all_tasks(self) -> dict:
    #     task_list = self.tasks.get_object_list()
    #     return self.display_tasks(task_list)
