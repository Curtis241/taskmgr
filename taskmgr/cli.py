import sys

import click

from taskmgr.lib.client_lib import CliClient, SyncClient
from taskmgr.lib.google_tasks_api import GoogleTasksService
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task_sync import Importer, Exporter
from taskmgr.lib.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables

cli_client = CliClient()
logger = AppLogger("cli").get_logger()


@click.group()
def cli():
    pass


@cli.command("add")
@click.argument('text')
@click.option('--label', '-l', help="label for task", default=CommonVariables.default_label, type=str,
              metavar='<label>')
@click.option('--project', '-p', help="project for task", default=CommonVariables.default_project_name,
              type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default=CommonVariables.default_date_expression,
              type=str, metavar='<due_date>')
def add_task(**kwargs):
    if cli_client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"]) is not None:
        cli_client.group_tasks()


@cli.command("edit")
@click.argument('key', type=str)
@click.option('--text', '-t', help="text for task", default=None, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=None, type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=None, type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default=CommonVariables.default_date_expression,
              type=str, metavar='<due_date>')
def edit_task(**kwargs):
    if cli_client.edit_task(**kwargs) is not None:
        cli_client.group_tasks()


@cli.command("delete")
@click.argument('key', nargs=-1, required=True)
def delete_task(**kwargs):
    if cli_client.delete_task(kwargs["key"]) is not None:
        cli_client.group_tasks()


@cli.command("list")
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    cli_client.group_tasks(kwargs["group"])


@cli.command("show")
@click.option('--filter', '-f', help="Filter tasks by complete status, project, and label", metavar='<filter>',
              type=click.Choice(['incomplete', 'complete', 'project', 'label']))
@click.option('--value', '-v', help="Label or project value", metavar='<value>')
def show_tasks(**kwargs):
    cli_client.filter_tasks(**kwargs)


@cli.command("today")
def today():
    kwargs = {'filter': SortType.DueDate}
    cli_client.filter_tasks(**kwargs)


@cli.command("reschedule")
def reschedule():
    cli_client.reschedule_tasks()
    cli_client.group_tasks()


@cli.command("complete")
@click.argument('key', nargs=-1, required=True)
def complete_task(**kwargs):
    if cli_client.complete_task(kwargs["key"]) is not None:
        cli_client.group_tasks()


@cli.command("sync")
@click.option('--export', '-e', default=False, is_flag=True)
@click.option('--import', '-i', default=False, is_flag=True)
def sync(**kwargs):
    export_enabled = kwargs["export"]
    import_enabled = kwargs["import"]

    if export_enabled is False and import_enabled is False:
        logger.info("Nothing to do. Enable import and export using parameters")
        exit(-1)

    service = GoogleTasksService()
    tasks = Tasks()
    sync_client = SyncClient(Importer(service, tasks), Exporter(service, tasks))
    sync_client.sync(export_enabled, import_enabled)


if __name__ == "__main__":
    sys.exit(cli())
