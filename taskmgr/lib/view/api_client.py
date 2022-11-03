from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, task_list: list):
        return {"tasks": [dict(task) for task in task_list]}

    def display_invalid_index_error(self, index: int):
        return {"error": True, "detail": [{"loc": ["param", "index"]}], "msg": f"Provided index {index} is invalid",
                "type": "attribute_error"}

    def display_snapshots(self, snapshot_list: list):
        return {"snapshot": {"list": [dict(snapshot) for snapshot in snapshot_list]}}

    def display_attribute_error(self, param: str, message: str):
        return {"error": True, "detail": [{"loc": ["param", param]}], "msg": message, "type": "attribute_error"}

