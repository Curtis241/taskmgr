import sys

import click

from taskmgr.lib.model.google_tasks_service import GoogleTasksService
from taskmgr.lib.presenter.gtask_project_api import GTasksListAPI
from taskmgr.lib.presenter.gtasks_api import GTasksAPI


@click.group()
def gtask_cli():
    pass


@gtask_cli.command("get")
@click.option('--list_title', '-l', help="Title of Tasklist", metavar='<list_title>')
@click.option('--task_title', '-t', help="Title of Task", metavar='<task_title>')
def get_task(**kwargs):
    service = GoogleTasksService()
    taskslist_api = GTasksListAPI(service)
    taskslist = taskslist_api.get(kwargs.get('list_title'))
    tasks_api = GTasksAPI(taskslist.id, service)
    print(dict(tasks_api.get(kwargs.get('task_title'))))


if __name__ == "__main__":
    sys.exit(gtask_cli())
