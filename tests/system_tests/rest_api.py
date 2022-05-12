import requests

from taskmgr.lib.view.client_args import *


class RestApi:

    def __init__(self):
        self.__basename = "http://localhost:8000/"

    def __build_path(self, path: str) -> str:
        return f"{self.__basename}{path}"

    @staticmethod
    def __parse_response(response: requests.Response):
        response.raise_for_status()
        if response.status_code in [200, 201]:
            return response.json()

    def get(self, path: str) -> dict:
        with requests.Session() as session:
            response = session.get(self.__build_path(path))
            return self.__parse_response(response)

    def post(self, path: str, data: dict):
        with requests.Session() as session:
            response = session.post(self.__build_path(path), json=data)
            return self.__parse_response(response)

    def put(self, path: str, data: dict = None):
        with requests.Session() as session:
            if data:
                response = session.put(self.__build_path(path), json=data)
            else:
                response = session.put(self.__build_path(path))
            return self.__parse_response(response)

    def delete(self, path: str):
        with requests.Session() as session:
            response = session.delete(self.__build_path(path))
            return self.__parse_response(response)


class Project(RestApi):

    def __init__(self):
        super().__init__()

    def get_list(self) -> dict:
        return self.put("unique/project")


class Label(RestApi):

    def __init__(self):
        super().__init__()

    def get_list(self) -> dict:
        return self.put("unique/label")


class Task(RestApi):

    def __init__(self):
        super().__init__()

    def get_task(self, index: str) -> dict:
        return self.get(f"tasks/task/{index}")

    def delete_task(self, index: str) -> dict:
        return self.delete(f"tasks/task/delete/{index}")

    def undelete_task(self, index: str) -> dict:
        return self.delete(f"tasks/task/undelete/{index}")

    def complete_task(self, index: str) -> dict:
        return self.put(f"tasks/task/complete/{index}")

    def incomplete_task(self, index: str) -> dict:
        return self.put(f"tasks/task/incomplete/{index}")


class Tasks(RestApi):

    def __init__(self):
        super().__init__()

    def get_all(self) -> dict:
        return self.get("tasks")

    def add(self, name: str, label: str, project: str, due_date: str) -> dict:
        args = AddArgs(name=name, label=label, project=project, due_date=due_date)
        return self.post("tasks", args.dict())

    def edit(self, index: int, name: str, project: str, label: str, due_date: str) -> dict:
        args = EditArgs(index=index, name=name, project=project, label=label, due_date=due_date)
        return self.put("tasks", args.dict())

    def remove_all(self) -> dict:
        return self.delete("tasks")

    def reschedule(self):
        self.put("reschedule/")

    def group_by_label(self):
        return self.put("group/label")

    def group_by_project(self):
        return self.put("group/project")

    def group_by_due_date(self):
        return self.put("group/due_date")

    def count_all(self) -> dict:
        return self.get("count_all")

    def count_by_due_date(self, due_date: str) -> dict:
        args = DueDateArgs(due_date=due_date)
        return self.put("count/due_date", args.dict())

    def count_by_project(self, project_name: str) -> dict:
        args = ProjectArgs(project=project_name)
        return self.put("count/project", args.dict())

    def count_by_due_date_range(self, min_date: str, max_date: str) -> dict:
        args = DueDateRangeArgs(min_date=min_date, max_date=max_date)
        return self.put("count/due_date_range", args.dict())

    def filter_by_project(self, project_name: str) -> dict:
        args = ProjectArgs(project=project_name)
        return self.put("count/project", args.dict())

    def filter_by_label(self, label: str) -> dict:
        args = LabelArgs(label=label)
        return self.put("count/label", args.dict())

    def filter_by_name(self, name: str) -> dict:
        args = NameArgs(name=name)
        return self.put("count/name", args.dict())

    def filter_by_due_date(self, due_date: str) -> dict:
        args = DueDateArgs(due_date=due_date)
        return self.put("count/due_date", args.dict())

    def filter_by_status(self, status: str) -> dict:
        args = StatusArgs(status=status)
        return self.put("count/status", args.dict())

    def filter_by_due_date_range(self, min_date: str, max_date: str) -> dict:
        args = DueDateRangeArgs(min_date=min_date, max_date=max_date)
        return self.put("count/due_date_range", args.dict())




