import sys
import re
import click

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database import DatabaseManager
from taskmgr.lib.model.google_tasks_service import GoogleTasksService
from taskmgr.lib.presenter.file_exporter import FileExporter
from taskmgr.lib.presenter.snapshots import Snapshots
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, GoogleTasksExporter
from taskmgr.lib.presenter.tasks import SortType, Tasks
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient

mgr = DatabaseManager()
tasks_db = mgr.get_database(DatabaseManager.TASKS_DB)
snapshots_db = mgr.get_database(DatabaseManager.SNAPSHOT_DB)
tasks = Tasks(tasks_db)
snapshots = Snapshots(snapshots_db)
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


@cli.group("filter")
def task_filter(): pass


@task_filter.command("project", help="Filter tasks by project")
@click.option('--value', help="Finds complete project name")
def filter_tasks_by_project(**kwargs):
    kwargs["filter"] = SortType.Project
    cli_client.filter(**kwargs)


@task_filter.command("status", help="Filter tasks by status")
@click.option('--value', type=click.Choice(['incomplete', 'complete']))
def filter_tasks_by_status(**kwargs):
    kwargs["filter"] = SortType.Status
    cli_client.filter(**kwargs)


@task_filter.command("text", help="Filter tasks by text")
@click.option('--value', help="Finds complete or partial string")
def filter_tasks_by_text(**kwargs):
    kwargs["filter"] = SortType.Text
    cli_client.filter(**kwargs)


@task_filter.command("label", help="Filter tasks by label")
@click.option('--value', help='Finds complete label string')
def filter_tasks_by_label(**kwargs):
    kwargs["filter"] = SortType.Label
    cli_client.filter(**kwargs)


class DateFormatString(click.ParamType):
    name = 'date-format'

    def convert(self, value, param, ctx):
        found = re.match(r'\d{4}-\d{2}-\d{2}', value)

        if not found:
            self.fail(
                f'{value} is not a date string (ie. 2019-01-21)',
                param,
                ctx,
            )

        return value


@task_filter.command("due_dates", help="Filter tasks by date range")
@click.option('--min_date', help='Minimum date', type=DateFormatString())
@click.option('--max_date', help='Maximum date', type=DateFormatString())
def filter_tasks_by_date_range(**kwargs):
    kwargs["filter"] = SortType.DueDateRange
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


@cli.command("reset", help="Resets the done status")
@click.argument('index', nargs=-1, required=True, type=int)
def pick_task(**kwargs):
    cli_client.reset_tasks(kwargs.get("index"))


@cli.command("count", help="Counts the tasks")
def count():
    cli_client.count()


@cli.command("import", help="Imports the tasks from the Google Tasks service")
def import_tasks():
    cli_client.import_tasks(GoogleTasksImporter(GoogleTasksService(), tasks))


@cli.command("export", help="Exports the tasks to the Google Tasks service")
def export_tasks():
    cli_client.export_tasks(GoogleTasksExporter(GoogleTasksService(), tasks))


@cli.command("defaults", help="Sets the default variables")
@click.option('--default_date_expression', help="Sets the default date expression (ie. today, empty)",
              type=click.Choice(['today', 'empty']))
@click.option('--default_project_name', help="Sets the default project name", type=str, default=None)
@click.option('--default_label', help="Sets the default label", type=str, default=None)
@click.option('--default_text_field_length', help="Sets the default text field length", type=str, default=None)
@click.option('--recurring_month_limit', help="Sets the recurring month limit", type=int, default=None)
@click.option('--enable_redis', help="Enables connection to the local redis database",
              type=click.Choice(['True', 'False']))
@click.option('--redis_port', help="Port for redis database", type=int, default=None)
@click.option('--redis_host', help="IPv4 address for redis database", type=str, default=None)
def set_defaults(**kwargs):
    cli_client.set_default_variables(**kwargs)
    cli_client.list_default_variables()


if __name__ == "__main__":
    sys.exit(cli())
