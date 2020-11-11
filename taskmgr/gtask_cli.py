import sys

import click

from taskmgr.lib.model.google_tasks_service import GoogleTasksService
from taskmgr.lib.presenter.gtask_project_api import GTasksProjectAPI
from taskmgr.lib.presenter.gtasks_api import GTasksAPI

service = GoogleTasksService()
taskslist_api = GTasksProjectAPI(service)

@click.group()
def gtask_cli():
    pass


@gtask_cli.command("get")
@click.option('--taskslist_title', '-l', help="Title of Tasklist", metavar='<tasklist_title>')
@click.option('--task_title', '-t', help="Title of Task", metavar='<task_title>')
def get_task(**kwargs):
    if "tasklist_title" and "task_title" in kwargs:
        taskslist = taskslist_api.get(kwargs.get('tasklist_title'))
        tasks_api = GTasksAPI(taskslist.id, service)
        print(dict(tasks_api.get_by_title(kwargs.get('task_title'))))
    else:
        print("Must have project and task name")


@gtask_cli.command("list_tasks")
@click.option('--list_title', '-l', help="Title of Tasklist", metavar='<list_title>')
def get_task(**kwargs):
    if "list_title" in kwargs:
        taskslist = taskslist_api.get(kwargs.get('list_title'))
        tasks_api = GTasksAPI(taskslist.id, service)
        for task in tasks_api.list():
            print(dict(task))
    else:
        print("Must have project name")


@gtask_cli.command("list_tasklists")
def list_tasklists(**kwargs):
    tasklists = taskslist_api.list()
    for tasklist in tasklists:
        print(dict(tasklist))

if __name__ == "__main__":
    sys.exit(gtask_cli())
