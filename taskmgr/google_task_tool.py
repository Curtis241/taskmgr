import sys

import click

from taskmgr.lib.google_tasks_api import GoogleTasksService, TasksListAPI, TasksAPI


@click.group()
def google_task_tool():
    pass


@google_task_tool.command("get")
@click.option('--list_title', '-l', help="Title of Tasklist", metavar='<list_title>')
@click.option('--task_title', '-t', help="Title of Task", metavar='<task_title>')
def get_task(**kwargs):
    service = GoogleTasksService()
    taskslist_api = TasksListAPI(service)
    taskslist = taskslist_api.get(kwargs.get('list_title'))
    tasks_api = TasksAPI(taskslist.id, service)
    print(dict(tasks_api.get(kwargs.get('task_title'))))


if __name__ == "__main__":
    sys.exit(google_task_tool())
