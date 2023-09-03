import ast
from typing import List

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.sync import SyncResultsList, ImportActions, SyncAction


class TaskImporter:
    logger = AppLogger("importer").get_logger()

    def __init__(self, tasks):
        self.__tasks = tasks

    @staticmethod
    def convert(obj_list: list) -> List[Task]:
        task_list = list()

        for obj_dict in obj_list:
            task = Task(obj_dict["name"])
            for key, value in obj_dict.items():
                if key == "deleted":
                    value = ast.literal_eval(value)
                    task.deleted = value
                elif key == "due_date":
                    task.due_date = value
                elif key == "done":
                    value = ast.literal_eval(value)
                    task.completed = value
                else:
                    setattr(task, key, value)
            task_list.append(task)
        return task_list

    def import_objects(self, remote_obj_list, bulk_save: bool = False) -> SyncResultsList:
        """
        Manage task import from csv file
        :param remote_obj_list: Tasks contained in file
        :param bulk_save: Save all changes after sorting each Task object
        :return ImportResultsList:
        """
        assert type(remote_obj_list) is list
        sync_results = SyncResultsList()
        object_list = list()

        for remote_task in remote_obj_list:
            assert type(remote_task) is Task

            local_task = self.__tasks.get_task_by_id(remote_task.unique_id)
            action = ImportActions(local_task, remote_task)

            if action.can_delete():
                TaskImporter.logger.debug("deleting task")
                object_list.append(self.__tasks.delete(local_task, not bulk_save))
                sync_results.append(SyncAction.DELETED)

            elif action.can_update():
                TaskImporter.logger.debug("updating task")
                object_list.append(self.__tasks.replace(local_task, remote_task, not bulk_save))
                sync_results.append(SyncAction.UPDATED)

            elif action.can_insert():
                TaskImporter.logger.debug("inserting task")
                object_list.append(self.__tasks.insert(remote_task, not bulk_save))
                sync_results.append(SyncAction.ADDED)

            else:
                sync_results.append(SyncAction.SKIPPED)
                TaskImporter.logger.debug(f"Skipping local task {remote_task.name}")

        if object_list and bulk_save is True:
            TaskImporter.logger.info(f"Saving all {len(object_list)} tasks to database")
            self.__tasks.update_all(object_list)

        return sync_results



