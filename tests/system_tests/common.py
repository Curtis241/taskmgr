from dpath import util


class Common:
    @staticmethod
    def verify_structure(response: dict) -> bool:
        assert type(response) is dict
        return "tasks" in response

    @staticmethod
    def count_tasks(response: dict) -> int:
        task_list = util.get(response, "tasks")
        return len(task_list)


