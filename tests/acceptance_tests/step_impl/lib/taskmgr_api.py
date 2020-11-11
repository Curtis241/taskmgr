from tests.acceptance_tests.step_impl.lib.rest_api import RestApi


class TaskmgrApi:

    def __init__(self):
        self.rest_api = RestApi()

    def add_task(self, name, project, label, due_date) -> dict:
        data = {"name": name, "project": project,
                "label": label, "due_date": due_date}
        return self.rest_api.post("/task/add", data)

    def list_tasks(self) -> dict:
        return self.rest_api.get("/tasks/list")
