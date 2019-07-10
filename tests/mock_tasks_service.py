from taskmgr.lib.google_tasks_api import TasksService


class MockTasksService(TasksService):

    def __init__(self):
        self.tasklist = {'kind': 'tasks#taskLists',
                         'items': [
                             {'kind': 'tasks#taskList', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDow', 'title': 'My Tasks',
                              'updated': '2019-05-25T06:12:12.000Z'},
                             {'kind': 'tasks#taskList',
                              'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDc1NDgzNjgwOTk2NTE0Mzc4Nzk6MA', 'title': 'Home',
                              'updated': '2019-05-20T20:22:30.000Z'}]}
        self.task = {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo0MzA3Njk5NDEzOTQyNDEy',
                     'etag': '"84_7Cubo3y98GMV9bE3zQclHxhc/LTQ0MzUxNDg1Mw"', 'title': 'Task2.3',
                     'updated': '2019-05-16T04:11:24.000Z',
                     'parent': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjQ3MDI0MzU0NTY4MzU1',
                     'position': '00000000001503238552',
                     'status': 'needsAction'}
        self.tasks = {'kind': 'tasks#tasks', 'etag': '"84_7Cubo3y98GMV9bE3zQclHxhc/LTE4NTgxOTE5OQ"', 'items': [
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjA2MDM5MTI4ODkyNDYz', 'title': 'Task1',
             'updated': '2019-05-25T06:12:12.000Z',
             'position': '00000000000000000000', 'status': 'needsAction', 'due': '2019-05-25T00:00:00.000Z'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4OTU3OTc2NTQ1OTMxNjU1', 'title': 'Task4',
             'updated': '2019-05-17T03:48:30.000Z',
             'position': '00000000000000000001', 'notes': 'label: @all, priority: 1', 'status': 'needsAction'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo0MzA3Njk5NDEzOTQyNDEy', 'title': 'Task2.3',
             'updated': '2019-05-16T04:11:24.000Z',
             'parent': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjQ3MDI0MzU0NTY4MzU1', 'position': '00000000000000000000',
             'status': 'needsAction'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDoxODUzMDEyMTQ3MDU2ODc4', 'title': 'Task3',
             'updated': '2019-05-16T04:08:09.000Z',
             'position': '00000000000000000002', 'status': 'needsAction'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDozOTY2OTk1NzQxMDgxMjcw', 'title': 'Task2.2',
             'updated': '2019-05-16T04:07:47.000Z',
             'parent': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjQ3MDI0MzU0NTY4MzU1', 'position': '00000000000000000002',
             'status': 'needsAction'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo5NDU1MzM5MzU3OTUxMzM2', 'title': 'Task2.1',
             'updated': '2019-05-16T04:07:38.000Z',
             'parent': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjQ3MDI0MzU0NTY4MzU1', 'position': '00000000000000000001',
             'status': 'needsAction'},
            {'kind': 'tasks#task', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDo4MjQ3MDI0MzU0NTY4MzU1', 'title': 'Task2',
             'updated': '2019-05-16T04:07:15.000Z',
             'position': '00000000000000000003', 'status': 'needsAction'}]}

        self.empty_tasks = {'kind': 'tasks#tasks', 'etag': '"84_7Cubo3y98GMV9bE3zQclHxhc/LTE4NTgxOTE5OQ"', 'items': []}

        self.__return_empty_tasks = False

    @property
    def return_empty_tasks(self):
        return self.__return_empty_tasks

    @return_empty_tasks.setter
    def return_empty_tasks(self, enable):
        self.__return_empty_tasks = enable

    def list_tasklist(self):
        return self.tasklist

    def get_tasklist(self, tasklist_id):
        return self.tasklist

    def insert_tasklist(self, tasklist_title):
        return {'kind': 'tasks#taskList', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDow', 'title': tasklist_title,
                'updated': '2019-05-25T06:12:12.000Z'}

    def delete_tasklist(self, tasklist_id):
        return None

    def update_tasklist(self, tasklist_id, tasklist):
        return {'kind': 'tasks#taskList', 'id': 'MTI1NzI0NTEyMjAyNDQyNjk3MzQ6MDow', 'title': tasklist["title"],
                'updated': '2019-05-25T06:12:12.000Z'}

    def list_tasks(self, tasklist_id):
        if self.return_empty_tasks:
            return self.empty_tasks
        else:
            return self.tasks

    def insert_task(self, tasklist_id, task):
        return self.task

    def clear_tasks(self, tasklist_id):
        return self.task

    def delete_task(self, tasklist_id, task_id):
        return self.task

    def update_task(self, tasklist_id, task_id, task):
        return dict(task)
