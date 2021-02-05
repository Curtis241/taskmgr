import socket
from tests.acceptance_tests.step_impl.lib.rest_api import RestApi


class TaskmgrApi:

    def __init__(self):
        self.rest_api = RestApi()

    def is_connected(self):
        try:
            socket.create_connection((self.rest_api.ip_address,
                                      self.rest_api.port), 30)
            return True
        except ConnectionRefusedError:
            print(f"Cannot connect to "
                  f"{self.rest_api.ip_address}:{self.rest_api.port}")
            return False

    def add_task(self, name, project, label, due_date) -> dict:
        if self.is_connected():
            data = {"name": name, "project": project,
                    "label": label, "due_date": due_date}
            return self.rest_api.post("/task/add", data)

    def list_tasks(self) -> dict:
        if self.is_connected():
            return self.rest_api.get("/tasks/list")
