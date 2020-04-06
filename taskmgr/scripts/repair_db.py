from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database import RedisDatabase
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.tasks import Tasks
from taskmgr.lib.variables import CommonVariables


class Issues:
    def __init__(self):
        self.empty_due_date = 0
        self.has_due_dates_property = 0
        self.total_count = 0

    def exist(self):
        return self.empty_due_date > 0 or self.has_due_dates_property > 0

    def get_report(self):
        return f"empty due date count: {self.empty_due_date}," \
               f" deprecated repeated task count: {self.has_due_dates_property}," \
               f" total tasks checked: {self.total_count}"


class RepairDb:
    """
    A data model change was introduced in the 0.1.7 release. The Task.due_dates property was deprecated because the
    repeated task type caused problems in defining when a task was complete. If a task has multiple due_dates it is
    only really done when all due_date objects have been completed, which is not what a user would expect. Every
    due_date should be considered done when it is completed, not when all due_dates are completed.
    I decided to only support a single Task.due_date object which resolves the issue.
    """

    def __init__(self):
        self.__logger = AppLogger("repair_db").get_logger()
        self.__variables = CommonVariables()

    def __get_database(self):
        if self.__variables.enable_redis:
            redis_db = RedisDatabase(self.__variables.redis_host, self.__variables.redis_port)
            self.__logger.info("Attempting to connect to redis")
            if redis_db.exists():
                return redis_db
            else:
                self.__logger.error("Cannot connect to redis")
        else:
            self.__logger.info("Redis database support is disabled. Use defaults command to enable.")

    @staticmethod
    def __fix_due_dates(redis_db):
        task_list = []
        for task in Tasks(redis_db).get_object_list():
            if len(task.due_dates) == 1:
                task.due_date = task.due_dates[0]
            else:
                for due_date in task.due_dates:
                    new_task = Task(task.text)
                    new_task.deleted = task.deleted
                    new_task.due_date = due_date
                    task_list.append(new_task)

            task.due_dates = []
            task_list.append(task)
        return task_list

    @staticmethod
    def count_issues(redis_db) -> Issues:
        issues = Issues()
        for task in Tasks(redis_db).get_object_list():
            if len(task.due_dates) > 1 and len(task.due_date.date_string) == 0:
                issues.empty_due_date += 1
            if len(task.due_dates) > 1:
                issues.has_due_dates_property += 1
            issues.total_count += 1

        return issues

    def fix(self, can_repair=False):
        redis_db = self.__get_database()
        if redis_db is not None:
            self.__logger.info("Checking database for issues")
            issues = self.count_issues(redis_db)

            if can_repair:
                if issues.exist():
                    task_list = self.__fix_due_dates(redis_db)
                    redis_db.set(task_list)
                    self.__logger.info(f"Fixed: {issues.get_report()}")
                else:
                    self.__logger.info(f"Nothing to fix: {issues.get_report()}")
            else:
                self.__logger.info(f"Check report: {issues.get_report()}")

