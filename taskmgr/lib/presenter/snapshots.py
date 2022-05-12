from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.presenter.tasks import Tasks


class Snapshots:
    logger = AppLogger("snapshots").get_logger()

    def __init__(self, tasks: Tasks):
        self.__tasks = tasks
        self.__task_list = []

    @staticmethod
    def __summarize(task_list: list) -> Snapshot:
        snapshot = Snapshot()
        for task in task_list:
            if task.deleted:
                snapshot.deleted += 1
            elif task.completed:
                snapshot.completed += 1
            elif not task.completed:
                snapshot.incomplete += 1

            snapshot.total_time = snapshot.total_time + task.time_spent
            snapshot.count = len(task_list)
            snapshot.due_date = task.due_date

            try:
                snapshot.average_time = round(float(snapshot.total_time / snapshot.count), 2)
            except ZeroDivisionError:
                snapshot.average_time = 0

        return snapshot

    def get_snapshot(self) -> tuple:

        if len(self.__task_list) > 0:
            # snapshot object has index and due_date that are not needed
            # for the summary because there is always one object.
            summary = self.__summarize(self.__task_list)

            snapshot_list = []
            due_date_list = list(set([task.due_date for task in self.__task_list]))
            for index, due_date in enumerate(due_date_list, start=1):
                task_list = self.__tasks.get_tasks_by_date(due_date)
                snapshot = self.__summarize(task_list)
                snapshot.index = index
                snapshot_list.append(snapshot)

            return summary, sorted(snapshot_list, key=lambda sn: sn.due_date)
        else:
            return Snapshot(), list()

    def count_all_tasks(self):
        self.__task_list = self.__tasks.get_task_list()

    def count_tasks_by_due_date_range(self, min_date: str, max_date: str):
        self.__task_list = self.__tasks.get_tasks_within_date_range(min_date, max_date)

    def count_tasks_by_due_date(self, due_date: str):
        self.__task_list = self.__tasks.get_tasks_by_date(due_date)

    def count_tasks_by_project(self, project_name: str):
        self.__task_list = self.__tasks.get_tasks_by_project(project_name)

    def count_tasks_by_label(self, label: str):
        self.__task_list = self.__tasks.get_tasks_by_label(label)

    def count_tasks_by_name(self, name: str):
        self.__task_list = self.__tasks.get_tasks_matching_name(name)

