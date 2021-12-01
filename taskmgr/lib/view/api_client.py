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

    @staticmethod
    def display_attribute_error(attribute_name: str, message: str):
        return {"detail": [{"loc": ["param", attribute_name]}], "msg": message, "type": "attribute_error"}

    def display_snapshots(self, snapshots: Snapshots):
        summary, snapshot_list = snapshots.get_snapshot()
        return {"snapshot": {"summary": summary, "list": [dict(snapshot) for snapshot in snapshot_list]}}

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


if __name__ == "__main__":
    from taskmgr.lib.model.database_manager import DatabaseManager
    api_client = ApiClient(DatabaseManager())
    api_client.remove_all_tasks()
    api_client.add_task("task1", "project1", "label1", "2021-07-11")
    api_client.add_task("task2", "project1", "label1", "2021-07-15")
    api_client.add_task("task3", "project1", "label1", "2021-07-21")
    api_client.add_task("task4", "project1", "label1", "2021-07-13")
    #print(api_client.count_tasks_by_due_date("2021-07-11"))
    print(api_client.count_tasks_by_due_date_range("2021-07-10", "2021-07-14"))