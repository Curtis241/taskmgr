from taskmgr.lib.database import FileDatabase
from taskmgr.lib.date_generator import DateGenerator
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import SortType


class CliClient(object):

    def __init__(self, database=None):

        if database is None:
            self.db = FileDatabase()
        else:
            self.db = database

        self.tasks = self.db.retrieve()
        self.views = [{"action": "group", "sort_type": SortType.Label, "func": self.group_by_label},
                      {"action": "group", "sort_type": None, "func": self.display_all_tasks},
                      {"action": "group", "sort_type": SortType.Project, "func": self.group_by_project},
                      {"action": "filter", "sort_type": SortType.Label, "func": self.filter_by_label},
                      {"action": "filter", "sort_type": SortType.Project, "func": self.filter_by_project}]

    def add_task(self, text, label, project, due_date):
        task = Task(text)
        task.label = label
        task.project = project
        task.due_date = DateGenerator(due_date).get_dates()
        self.tasks.add(task)
        self.db.save(self.tasks)
        return self.tasks

    def delete_task(self, task_index):
        assert type(task_index) is int
        self.tasks.delete(task_index)
        self.db.save(self.tasks)

    def complete_task(self, task_index):
        assert type(task_index) is int
        self.tasks.complete(task_index)
        self.db.save(self.tasks)

    def list_tasks(self, sort_type=None):
        for view_dict in self.views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "group":
                func = view_dict["func"]
                return func(self.tasks)

    def list_labels(self):
        print("Labels: {}".format(list(self.tasks.unique(SortType.Label))))

    def list_projects(self):
        print("Projects: {}".format(list(self.tasks.unique(SortType.Project))))

    @staticmethod
    def filter_by_label(tasks):
        pass

    @staticmethod
    def filter_by_project(tasks):
        pass

    @staticmethod
    def group_by_label(tasks):
        for label in tasks.unique(SortType.Label):
            print("Label: {}".format(label))
            for task in tasks.get_list_by_type(SortType.Label, label):
                if task.is_complete:
                    print("#{} Done - {} ".format(task.index, task.text))
                else:
                    print("#{} - {} ".format(task.index, task.text))
        return tasks

    @staticmethod
    def group_by_project(tasks):
        for project in tasks.unique(SortType.Project):
            print("Project: {}".format(project))
            for task in tasks.get_list_by_type(SortType.Project, project):
                if task.is_complete:
                    print("#{} Done - {} ".format(task.index, task.text))
                else:
                    print("#{} - {} ".format(task.index, task.text))
        return tasks

    @staticmethod
    def display_all_tasks(tasks):
        for task in tasks.get_list():
            if task.is_complete:
                print("#{} Done - {} [project:{}, label:{}, due_date:{}]".format(task.index, task.text, task.project,
                                                                                 task.label, task.due_date))
            else:
                print("#{} - {} [project:{}, label:{}, due_date:{}]".format(task.index, task.text, task.project,
                                                                            task.label, task.due_date))
        return tasks

    def remove_tasks(self):
        self.db.remove()
