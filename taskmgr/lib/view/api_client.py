from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, task_list: list):
        return {"tasks": [dict(task) for task in task_list]}

    def display_invalid_index_error(self, index: int):
        return {"tasks": [], "message": f"Provided index {index} is invalid"}

    def display_snapshots(self, snapshot_list: list):
        return {"snapshots": [dict(snapshot) for snapshot in snapshot_list]}

    def add_task(self, text: str, label: str, project: str, date_expression: str) -> dict:
        return self.display_tasks(self.tasks.add(text, label, project, date_expression))

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
