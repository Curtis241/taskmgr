from taskmgr.lib.google_tasks_api import TasksListAPI, TasksAPI, TaskList, Task


class Sync:

    def __init__(self):
        self.tasks_list_api = TasksListAPI()
        self.tasks_api = TasksAPI()

    def from_json(self):
        """
        Converts json object returned by the Google Tasks service
        into local objects
        :return: list of TaskList objects
        """
        task_list = list()
        for task_list_dict in self.tasks_list_api.list():
            print(task_list_dict)
            parent_obj = TaskList()
            for key in task_list_dict:
                setattr(parent_obj, key, task_list_dict[key])

            if len(parent_obj.id) > 0:
                child_obj = Task()
                for tasks_dict in self.tasks_api.get(parent_obj.id):
                    print(tasks_dict)
                    for key in tasks_dict:
                        setattr(child_obj, key, tasks_dict[key])
                parent_obj.append(child_obj)

            task_list.append(parent_obj)

        return task_list