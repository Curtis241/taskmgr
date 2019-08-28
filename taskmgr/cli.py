import sys

import click

from taskmgr.lib.client_lib import CliClient, SyncClient
from taskmgr.lib.database import JsonFileDatabase
from taskmgr.lib.file_exporter import FileExporter
from taskmgr.lib.google_tasks_api import GoogleTasksService
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.task_sync import Importer, Exporter
from taskmgr.lib.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables

tasks = Tasks(JsonFileDatabase("tasks_db"))
cli_client = CliClient(tasks, FileExporter())
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
    cli_client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])


@cli.command("edit")
@click.argument('index', type=int)
@click.option('--text', '-t', help="text for task", default=CommonVariables.default_text, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=CommonVariables.default_label,
              type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=CommonVariables.default_project_name,
              type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default=CommonVariables.default_date_expression,
              type=str, metavar='<due_date>')
def edit_task(**kwargs):
    cli_client.edit_task(kwargs.get("index"), kwargs.get("text"), kwargs.get("project"),
                         kwargs.get("label"), kwargs.get("due_date"))


@cli.command("delete")
@click.argument('index', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete_tasks(kwargs.get("index"))


@cli.command("list")
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    cli_client.group(**kwargs)


@cli.command("filter")
@click.option('--type', '-t', 'filter', help="Filter tasks by complete status, project, text, and label",
              metavar='<filter>', type=click.Choice(['incomplete', 'complete', 'project', 'label', 'text']))
@click.option('--value', '-v', help="Label or project value", metavar='<value>')
@click.option('--export_path', '-p', help="Destination path to save markdown file.", metavar='<export_path>')
def filter_tasks(**kwargs):
    cli_client.filter(**kwargs)


@cli.command("today")
@click.option('--export_path', '-p', help="Destination path to save markdown file.", metavar='<export_path>')
def today(**kwargs):
    kwargs["filter"] = SortType.DueDate
    cli_client.filter(**kwargs)


@cli.command("reschedule")
def reschedule():
    cli_client.reschedule_tasks()


@cli.command("complete")
@click.argument('index', nargs=-1, required=True, type=int)
def complete_task(**kwargs):
    cli_client.complete_tasks(kwargs.get("index"))


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
    sync_client = SyncClient(Importer(service, tasks), Exporter(service, tasks))
    sync_client.sync(export_enabled, import_enabled)


if __name__ == "__main__":
    sys.exit(cli())
