from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager, file_manager):
        super().__init__(db_manager, file_manager)

    def display_tasks(self, task_list: list, kwargs):
        return {"tasks": [dict(task) for task in task_list]}

    def display_snapshots(self, snapshot_list: list, kwargs):
        return {"snapshots": [dict(snapshot) for snapshot in snapshot_list]}