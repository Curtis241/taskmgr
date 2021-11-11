import requests


class RequestBody:

    def __init__(self, name: str, value1: str = None, value2: str = None):
        self.__name = name
        self.__value1 = value1
        self.__value2 = value2

    def __iter__(self):
        yield "name", self.__name

        if self.__value1 is not None:
            yield "value1", self.__value1

        if self.__value2 is not None:
            yield "value2", self.__value2


class TaskModel:
    def __init__(self, text: str, project: str, label: str, date_expression: str):
        self.index = None
        self.text = text
        self.project = project
        self.label = label
        self.date_expression = date_expression

    def __iter__(self):
        if self.index is not None:
            yield "index", self.index

        yield "text", self.text
        yield "project", self.project
        yield "label", self.label
        yield "date_expression", self.date_expression


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


class DefaultProperty(RestApi):

    def __init__(self):
        super().__init__()
        self.__path = "default/"

    def set_default_expression(self, value: str) -> dict:
        body = RequestBody("default_date_expression", value)
        return self.put(self.__path, dict(body))

    def set_default_label(self, value: str) -> dict:
        body = RequestBody("default_label", value)
        return self.put(self.__path, dict(body))

    def set_default_project(self, value: str) -> dict:
        body = RequestBody("default_project_name", value)
        return self.put(self.__path, dict(body))

    def set_month_limit(self, value: str) -> dict:
        body = RequestBody("default_month_limit", value)
        return self.put(self.__path, dict(body))


class Project(RestApi):

    def __init__(self):
        super().__init__()

    def get_list(self) -> dict:
        return self.put("unique/", dict(RequestBody("project")))


class Label(RestApi):

    def __init__(self):
        super().__init__()

    def get_list(self) -> dict:
        return self.put("unique/", dict(RequestBody("label")))


class Task(RestApi):

    def __init__(self):
        super().__init__()

    def get_task(self, index: str) -> dict:
        return self.get(f"tasks/task/{index}")

    def delete_task(self, uuid: str) -> dict:
        return self.delete(f"tasks/task/delete/{uuid}")

    def undelete_task(self, uuid: str) -> dict:
        return self.delete(f"tasks/task/undelete/{uuid}")

    def complete_task(self, uuid: str) -> dict:
        return self.put(f"tasks/task/complete/{uuid}")

    def incomplete_task(self, uuid: str) -> dict:
        return self.put(f"tasks/task/incomplete/{uuid}")


class Tasks(RestApi):

    def __init__(self):
        super().__init__()
        self.__group_path = "group/"
        self.__count_path = "count/"
        self.__filter_path = "filter/"

    def get_all(self) -> dict:
        return self.get("tasks")

    def add(self, text: str, project: str, label: str, date_expression: str) -> dict:
        return self.post("tasks", dict(TaskModel(text, project, label, date_expression)))

    def edit(self, index: str, text: str, project: str, label: str, date_expression: str) -> dict:
        model = TaskModel(text, project, label, date_expression)
        model.index = index
        return self.put("tasks", dict(model))

    def remove_all(self) -> dict:
        return self.delete("tasks")

    def reschedule(self):
        self.put("reschedule/")

    def group_by_label(self, label: str):
        return self.put(self.__group_path, dict(RequestBody("label", label)))

    def group_by_project(self, project: str):
        return self.put(self.__group_path, dict(RequestBody("project", project)))

    def group_by_due_date(self, due_date: str):
        return self.put(self.__group_path, dict(RequestBody("due_date", due_date)))

    def count_all(self) -> dict:
        return self.put(self.__count_path, dict(RequestBody("all")))

    def count_by_due_date(self, due_date: str) -> dict:
        return self.put(self.__count_path, dict(RequestBody("due_date", due_date)))

    def count_by_project(self, project_name: str) -> dict:
        return self.put(self.__count_path, dict(RequestBody("project", project_name)))

    def count_by_due_date_range(self, min_date: str, max_date: str) -> dict:
        return self.put(self.__count_path, dict(RequestBody("project", min_date, max_date)))

    def filter_by_project(self, project_name: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("project", project_name)))

    def filter_by_label(self, label: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("label", label)))

    def filter_by_text(self, text: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("text", text)))

    def filter_by_due_date(self, due_date: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("due_date", due_date)))

    def filter_by_status(self, status: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("status", status)))

    def filter_by_due_date_range(self, min_date: str, max_date: str) -> dict:
        return self.put(self.__filter_path, dict(RequestBody("due_date_range", min_date, max_date)))




