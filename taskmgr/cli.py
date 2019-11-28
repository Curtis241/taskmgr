import sys

import click

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database import JsonFileDatabase
from taskmgr.lib.model.google_tasks_service import GoogleTasksService
from taskmgr.lib.presenter.file_exporter import FileExporter
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, GoogleTasksExporter
from taskmgr.lib.presenter.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient

tasks = Tasks(JsonFileDatabase("tasks_db"))
snapshots = Snapshots(JsonFileDatabase("snapshots_db"))
cli_client = CliClient(tasks, snapshots, FileExporter())
logger = AppLogger("cli").get_logger()
vars = CommonVariables()


@click.group()
def cli():
    pass


@cli.command("add", help="Appends a task using the provided or default parameters")
@click.argument('text')
@click.option('--label', '-l', help="label for task", default=vars.default_label, type=str,
              metavar='<label>')
@click.option('--project', '-p', help="project for task", default=vars.default_project_name,
              type=str, metavar='<project>')
@click.option('--due_date', '-d', help="due date for task", default=vars.default_date_expression,
              type=str, metavar='<due_date>')
def add_task(**kwargs):
    cli_client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])


@cli.command("edit", help="Replaces the task parameters with the provided parameters")
@click.argument('index', type=int)
@click.option('--text', '-t', help="text for task", default=vars.default_text, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=vars.default_label,
              type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=vars.default_project_name,
              type=str, metavar='<project>')
@click.option('--due_date', '-d', help="due date for task", default=vars.default_date_expression,
              type=str, metavar='<due_date>')
def edit_task(**kwargs):
    cli_client.edit_task(kwargs.get("index"), kwargs.get("text"), kwargs.get("project"),
                         kwargs.get("label"), kwargs.get("due_date"))


@cli.command("delete", help="Toggles the delete parameter but keeps the object in the database. "
                            "Deleted tasks are hidden and do not appear in the lists.")
@click.argument('index', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete_tasks(kwargs.get("index"))


@cli.command("list", help="Displays all tasks by index order")
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    cli_client.group(**kwargs)


@cli.command("filter", help="Selects tasks using the filter type and provided value")
@click.option('--type', '-t', 'filter', help="Filter tasks by complete status, project, text, and label",
              metavar='<filter>', type=click.Choice(['incomplete', 'complete', 'project', 'label', 'text']))
@click.option('--value', '-v', help="Label or project value", metavar='<value>')
@click.option('--export_path', '-p', help="Destination path to save markdown file.", metavar='<export_path>')
def filter_tasks(**kwargs):
    cli_client.filter(**kwargs)


@cli.command("today", help="Lists only the tasks that have today's date")
@click.option('--export_path', '-p', help="Destination path to save markdown file.", metavar='<export_path>')
def today(**kwargs):
    kwargs["filter"] = SortType.DueDate
    cli_client.filter(**kwargs)


@cli.command("reschedule", help="Moves all tasks from the past to today")
def reschedule():
    cli_client.reschedule_tasks()


@cli.command("complete", help="Marks the task as done")
@click.argument('index', nargs=-1, required=True, type=int)
def complete_task(**kwargs):
    cli_client.complete_tasks(kwargs.get("index"))


@cli.command("copy", help="Duplicates a task and resets the done status")
@click.argument('index', nargs=-1, required=True, type=int)
def pick_task(**kwargs):
    cli_client.copy_tasks(kwargs.get("index"))


@cli.command("count", help="Counts the tasks")
def count():
    cli_client.count()


@cli.command("import_tasks", help="Imports the tasks from the Google Tasks service")
def import_tasks():
    cli_client.import_tasks(GoogleTasksImporter(GoogleTasksService(), tasks))


@cli.command("export_tasks", help="Exports the tasks to the Google Tasks service")
def export_tasks():
    cli_client.export_tasks(GoogleTasksExporter(GoogleTasksService(), tasks))


@cli.command("set_defaults", help="Sets the parameter defaults used by the add command")
@click.option('--default_date_expression', help="Sets the default date expression (ie. today, empty)", default=None)
@click.option('--default_project_name', help="Sets the default project name", default=None)
@click.option('--default_label', help="Sets the default label", default=None)
@click.option('--default_text_field_length', help="Sets the default text field length", default=None)
@click.option('--recurring_month_limit', help="Sets the recurring month limit", default=None)
def set_defaults(**kwargs):
    cli_client.set_defaults_and_display(**kwargs)


if __name__ == "__main__":
    sys.exit(cli())
