import re
import sys

import click

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.model.google_tasks_service import GoogleTasksService
from taskmgr.lib.presenter.file_exporter import FileExporter
from taskmgr.lib.presenter.task_sync import GoogleTasksImporter, GoogleTasksExporter
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient

cli_client = CliClient(DatabaseManager(), FileExporter())
logger = AppLogger("cli").get_logger()
variables = CommonVariables()


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


@click.group()
def cli():
    pass


@cli.command("add", help="Appends a task using the provided or default parameters")
@click.argument('text')
@click.option('--label', '-l', help="label for task", default=variables.default_label, type=str,
              metavar='<label>')
@click.option('--project', '-p', help="project for task", default=variables.default_project_name,
              type=str, metavar='<project>')
@click.option('--due_date', '-d', help="due date for task", default=variables.default_date_expression,
              type=str, metavar='<due_date>')
def add_task(**kwargs):
    cli_client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])


@cli.command("edit", help="Replaces the task parameters with the provided parameters")
@click.argument('index', type=int)
@click.option('--text', '-t', help="text for task", default=variables.default_text, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=variables.default_label,
              type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=variables.default_project_name,
              type=str, metavar='<project>')
@click.option('--due_date', '-d', help="due date for task", default=variables.default_date_expression,
              type=str, metavar='<due_date>')
def edit_task(**kwargs):
    cli_client.edit_task(kwargs.get("index"), kwargs.get("text"), kwargs.get("project"),
                         kwargs.get("label"), kwargs.get("due_date"))


@cli.command("delete", help="Toggles the delete parameter but keeps the object in the database. "
                            "Deleted tasks are hidden and do not appear in the lists.")
@click.argument('index', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete_tasks(kwargs.get("index"))


@cli.command("list", help="Lists all un-deleted tasks")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
@click.option('--all', is_flag=True)
def list_tasks(**kwargs):
    cli_client.display_all_tasks(**kwargs)


@cli.group("group", help="Groups tasks")
def task_group(): pass


@task_group.command("label")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def task_group_by_label(**kwargs):
    cli_client.group_by_label(**kwargs)


@task_group.command("project")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def task_group_by_project(**kwargs):
    cli_client.group_by_project(**kwargs)


@cli.group("filter", help="Filters tasks")
def task_filter(): pass


@task_filter.command("project")
@click.argument('project', type=str, required=True, metavar="<project>")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_project(**kwargs):
    cli_client.filter_by_project(**kwargs)


@task_filter.command("status")
@click.argument('status', type=click.Choice(['incomplete', 'complete']), required=True, metavar="<status>")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_status(**kwargs):
    cli_client.filter_by_status(**kwargs)


@task_filter.command("text")
@click.argument('text', type=str, required=True, metavar="<text>")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_text(**kwargs):
    cli_client.filter_by_text(**kwargs)


@task_filter.command("label")
@click.argument('label', type=str,  required=True, metavar="<label>")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_label(**kwargs):
    cli_client.filter_by_label(**kwargs)


@task_filter.command("date_range")
@click.option('--min_date', required=True, help='Minimum date', type=DateFormatString())
@click.option('--max_date', required=True, help='Maximum date', type=DateFormatString())
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_date_range(**kwargs):
    cli_client.filter_by_due_date_range(**kwargs)


@task_filter.command("date")
@click.argument('date', type=DateFormatString(), required=True, metavar="<date>")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>")
def filter_tasks_by_date(**kwargs):
    cli_client.filter_by_due_date(**kwargs)


@cli.command("today", help="Lists only the tasks that have today's date")
@click.option('--export', type=click.Choice([FileExporter.CSV, FileExporter.MARKDOWN]), metavar="<export>")
def today(**kwargs):
    cli_client.filter_by_today(**kwargs)


@cli.group("count", help="Displays task count")
def task_count(): pass


@task_count.command("all")
@click.option('--export', type=click.Choice([FileExporter.CSV]), metavar="<export>",
              help="Counts the deleted and un-deleted tasks")
def count_all_tasks(**kwargs):
    cli_client.count_all_tasks(**kwargs)


@task_count.command("date")
@click.argument('date', type=DateFormatString(), required=True, metavar="<date>")
def count_tasks_by_date(**kwargs):
    cli_client.count_by_due_date(**kwargs)


@task_count.command("date_range")
@click.option('--min_date', required=True, type=DateFormatString())
@click.option('--max_date', required=True, type=DateFormatString())
def count_tasks_by_date_range(**kwargs):
    cli_client.count_by_due_date_range(**kwargs)


@task_count.command("project")
@click.argument('project', type=str, required=True, metavar="<project>")
def count_tasks_by_project(**kwargs):
    cli_client.count_by_project(**kwargs)


@task_count.command("status")
@click.argument('status', type=click.Choice(['incomplete', 'complete']), required=True, metavar="<status>")
def count_tasks_by_status(**kwargs):
    cli_client.count_by_status(**kwargs)


@task_count.command("label")
@click.argument('label', type=str, required=True, metavar="<label>")
def count_tasks_by_label(**kwargs):
    cli_client.count_by_label(**kwargs)


@cli.command("reschedule", help="Moves all tasks from the past to today")
def reschedule():
    cli_client.reschedule_tasks()


@cli.command("complete", help="Marks the task as done")
@click.argument('index', nargs=-1, required=True, type=int)
def complete_task(**kwargs):
    cli_client.complete_tasks(kwargs.get("index"))


@cli.command("reset", help="Resets the done status")
@click.argument('index', nargs=-1, required=True, type=int)
def reset_task(**kwargs):
    cli_client.reset_tasks(kwargs.get("index"))


@cli.command("import", help="Imports the tasks from the Google Tasks service")
@click.argument('project', type=str, required=True, metavar="<project>")
def import_tasks(**kwargs):
    mgr = DatabaseManager()
    cli_client.import_tasks(GoogleTasksImporter(GoogleTasksService(), mgr.get_tasks_model()), kwargs.get("project"))


@cli.command("export", help="Exports the tasks to the Google Tasks service")
@click.argument('project', type=str, required=True, metavar="<project>")
def export_tasks(**kwargs):
    mgr = DatabaseManager()
    cli_client.export_tasks(GoogleTasksExporter(GoogleTasksService(), mgr.get_tasks_model()), kwargs.get("project"))


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
