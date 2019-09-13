import sys
import click

from taskmgr.lib.google_datastore import GoogleDatastoreService
from taskmgr.lib.google_tasks_api import GoogleTasksService, TasksListAPI, TasksAPI


@click.group()
def gtask_cli():
    pass


@gtask_cli.command("get")
@click.option('--list_title', '-l', help="Title of Tasklist", metavar='<list_title>')
@click.option('--task_title', '-t', help="Title of Task", metavar='<task_title>')
def get_task(**kwargs):
    service = GoogleTasksService()
    taskslist_api = TasksListAPI(service)
    taskslist = taskslist_api.get(kwargs.get('list_title'))
    tasks_api = TasksAPI(taskslist.id, service)
    print(dict(tasks_api.get(kwargs.get('task_title'))))


@gtask_cli.command("count")
def count_tasks(**kwargs):
    GoogleDatastoreService()


if __name__ == "__main__":
    sys.exit(gtask_cli())
