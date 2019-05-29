from prettytable import PrettyTable

from taskmgr.lib.database import FileDatabase
from taskmgr.lib.date_generator import Calendar, Today
from taskmgr.lib.task import Task
from taskmgr.lib.tasks import SortType


class CliClient(object):

    def __init__(self, database=None):
        self.calendar = Calendar()

        if database is None:
            self.db = FileDatabase()

            if not self.db.exists():
                self.db.make_db_path("tasks_db")
        else:
            self.db = database

        self.table = PrettyTable(["Id", "Done", "Text", "Project", "Label", "Due Date", "Until"])
        self.table.align["Id"] = "l"
        self.table.align["Done"] = "l"
        self.table.align["Text"] = "l"
        self.table.align["Project"] = "l"
        self.table.align["Label"] = "l"
        self.table.align["Due Date"] = "l"
        self.table.align["Until"] = "l"

        self.tasks = self.db.retrieve()
        self.views = [{"action": "group", "sort_type": SortType.Label, "func": self.__group_by_label},
                      {"action": "group", "sort_type": None, "func": self.__display_all_tasks},
                      {"action": "group", "sort_type": SortType.Project, "func": self.__group_by_project},
                      {"action": "filter", "sort_type": SortType.DueDate, "func": self.__filter_by_date}]

    def add_task(self, text, label, project, date_expression):
        task = Task(text)
        task.label = label
        task.project = project
        task.date_expression = date_expression
        self.tasks.add(task)
        self.db.save(self.tasks)
        return self.tasks

    def delete_task(self, index):
        assert type(index) is int
        self.tasks.delete(index)
        self.db.save(self.tasks)

    def edit_task(self, **kwargs):
        index = kwargs.get("index")
        assert type(index) is int
        task = self.tasks.edit(index, kwargs.get("text"), kwargs.get("label"), kwargs.get("project"),
                               kwargs.get("date_expression"))
        self.db.save(self.tasks)
        return task

    def complete_task(self, index):
        assert type(index) is int
        self.tasks.complete(index)
        self.db.save(self.tasks)

    def reschedule_tasks(self, today=Today()):
        self.tasks.reschedule(today)
        self.db.save(self.tasks)

    def group_tasks(self, sort_type=None):
        for view_dict in self.views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "group":
                func = view_dict["func"]
                return func(self.tasks)

    def filter_tasks(self, sort_type=None):
        for view_dict in self.views:
            if view_dict["sort_type"] == sort_type and view_dict["action"] == "filter":
                func = view_dict["func"]
                return func(self.tasks)

    def list_labels(self):
        print("Labels: {}".format(list(self.tasks.unique(SortType.Label))))

    def list_projects(self):
        print("Projects: {}".format(list(self.tasks.unique(SortType.Project))))

    @staticmethod
    def __filter_by_label(tasks):
        pass

    @staticmethod
    def __filter_by_project(tasks):
        pass

    def __filter_by_date(self, tasks):
        self.table.clear_rows()
        for task in tasks.get_list():
            if self.calendar.contains_today(task.due_dates):
                self.table.add_row(self.__get_row(task))
        print(self.table.get_string())
        return tasks

    @staticmethod
    def __get_row(task):
        return task.get_task_status()

    def __print_row(self):
        if len(self.table._rows) > 0:
            print(self.table.get_string())
        else:
            print("No rows to display. Use add command.")

    def __group_by_label(self, tasks):
        self.table.clear_rows()
        for label in tasks.unique(SortType.Label):
            for task in tasks.get_list_by_type(SortType.Label, label):
                self.table.add_row(self.__get_row(task))
        self.__print_row()
        return tasks

    def __group_by_project(self, tasks):
        self.table.clear_rows()
        for project in tasks.unique(SortType.Project):
            for task in tasks.get_list_by_type(SortType.Project, project):
                self.table.add_row(self.__get_row(task))
        self.__print_row()
        return tasks

    def __display_all_tasks(self, tasks):
        self.table.clear_rows()
        for task in tasks.get_list():
            self.table.add_row(self.__get_row(task))
        self.__print_row()
        return tasks

    def remove_tasks(self):
        self.db.remove()
