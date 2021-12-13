import sys

import click

from taskmgr.lib.logger import AppLogger
from taskmgr.lib.model.database_manager import DatabaseManager
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import CsvFileImporter
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient

cli_client = CliClient(DatabaseManager(), FileManager())
logger = AppLogger("cli").get_logger()
variables = CommonVariables()


class DateFormatString(click.ParamType):
    name = 'date-format'

    def convert(self, value, param, ctx):
        if variables.validate_date_format(value) is False:
            self.fail(
                f'{value} date string is not valid',
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
    cli_client.edit_task(kwargs.get("index"), kwargs.get("text"), kwargs.get("label"),
                         kwargs.get("project"), kwargs.get("due_date"))


@cli.command("list", help="Lists all tasks")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--all', is_flag=True, help="Shows deleted tasks")
def list_tasks(**kwargs):
    task_list = cli_client.list_all_tasks(kwargs.get("all"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@cli.command("delete", help="Soft delete")
@click.argument('index', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete_tasks(kwargs.get("index"))


@cli.command("undelete", help="Reverts deleted tasks")
@click.argument('index', nargs=-1, required=True, type=int)
def undelete_task(**kwargs):
    cli_client.undelete_tasks(kwargs.get("index"))


@cli.group("unique", help="Displays unique tasks")
def unique(): pass


@unique.command("label")
def unique_label_list():
    cli_client.list_labels()


@unique.command("project")
def unique_project_list():
    cli_client.list_projects()


@cli.group("group", help="Groups tasks")
def task_group(): pass


@task_group.command("label")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def task_group_by_label(**kwargs):
    task_list = cli_client.group_tasks_by_label()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_group.command("project")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def task_group_by_project(**kwargs):
    task_list = cli_client.group_tasks_by_project()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_group.command("due_date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def task_group_by_project(**kwargs):
    task_list = cli_client.group_tasks_by_due_date()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@cli.group("filter", help="Filters tasks")
def task_filter(): pass


@task_filter.command("project")
@click.argument('project', type=str, required=True, metavar="<project>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_project(**kwargs):
    task_list = cli_client.filter_tasks_by_project(kwargs.get("project"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_filter.command("status")
@click.argument('status', type=click.Choice(['incomplete', 'complete']), required=True, metavar="<status>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_status(**kwargs):
    task_list = cli_client.filter_tasks_by_status(kwargs.get("status"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_filter.command("text")
@click.argument('text', type=str, required=True, metavar="<text>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_text(**kwargs):
    task_list = cli_client.filter_tasks_by_text(kwargs.get("text"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_filter.command("label")
@click.argument('label', type=str, required=True, metavar="<label>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_label(**kwargs):
    task_list = cli_client.filter_tasks_by_label(kwargs.get("label"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_filter.command("date_range")
@click.option('--min_date', required=True, help='Minimum date', type=DateFormatString())
@click.option('--max_date', required=True, help='Maximum date', type=DateFormatString())
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_date_range(**kwargs):
    task_list = cli_client.filter_tasks_by_due_date_range(kwargs.get("min_date"), kwargs.get("max_date"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_filter.command("date")
@click.argument('date', type=str, required=True, metavar="<date>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_date(**kwargs):
    task_list = cli_client.filter_tasks_by_due_date(kwargs.get("date"))
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@cli.command("today", help="Lists only the tasks that have today's date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def today(**kwargs):
    task_list = cli_client.filter_tasks_by_today()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@cli.group("count", help="Displays task count")
def task_count(): pass


@task_count.command("all")
@click.option('--export', is_flag=True, help="Outputs all to csv file")
@click.option('--page', type=int, default=1)
def count_all_tasks(**kwargs):
    snapshot_list = cli_client.count_all_tasks(**kwargs)
    if kwargs.get("export"):
        cli_client.export_snapshots(snapshot_list)


@task_count.command("date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=1)
@click.argument('date', type=DateFormatString(), required=True, metavar="<date>")
def count_tasks_by_date(**kwargs):
    snapshot_list = cli_client.count_tasks_by_due_date(kwargs.get("date"), **kwargs)
    if kwargs.get("export"):
        cli_client.export_snapshots(snapshot_list)


@task_count.command("date_range")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--min_date', required=True, type=DateFormatString())
@click.option('--max_date', required=True, type=DateFormatString())
@click.option('--page', type=int, default=1)
def count_tasks_by_date_range(**kwargs):
    snapshot_list = cli_client.count_tasks_by_due_date_range(kwargs.get("min_date"), kwargs.get("max_date"), **kwargs)
    if kwargs.get("export"):
        cli_client.export_snapshots(snapshot_list)


@task_count.command("project")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=1)
@click.argument('project', type=str, required=True, metavar="<project>")
def count_tasks_by_project(**kwargs):
    snapshot_list = cli_client.count_tasks_by_project(kwargs.get("project"), **kwargs)
    if kwargs.get("export"):
        cli_client.export_snapshots(snapshot_list)


@cli.command("reschedule", help="Moves all tasks from the past to today")
def reschedule():
    cli_client.reschedule_tasks()


@cli.command("complete", help="Marks the task as done")
@click.argument('index', nargs=-1, required=True, type=int)
def complete_task(**kwargs):
    cli_client.complete_tasks(kwargs.get("index"))


@cli.command("incomplete", help="Marks the task as not done")
@click.argument('index', nargs=-1, required=True, type=int)
def reset_task(**kwargs):
    cli_client.reset_tasks(kwargs.get("index"))


@cli.command("import", help="Imports tasks from csv file")
@click.option('--path', type=str, required=True, metavar="<path>")
def import_tasks(**kwargs):
    mgr = DatabaseManager()
    cli_client.import_tasks(CsvFileImporter(mgr.get_tasks_model()), kwargs.get("path"))


@cli.command("defaults", help="Sets the default variables")
@click.option('--default_project_name', help="Sets the default project name", type=str, default=None)
@click.option('--default_label', help="Sets the default label", type=str, default=None)
@click.option('--default_text_field_length', help="Sets the default text field length", type=str, default=None)
@click.option('--recurring_month_limit', help="Sets the recurring month limit", type=int, default=None)
@click.option('--enable_redis', help="Enables connection to the local redis database",
              type=click.Choice(['True', 'False']))
@click.option('--redis_port', help="Port for redis database", type=int, default=None)
@click.option('--redis_host', help="IPv4 address for redis database", type=str, default=None)
@click.option('--max_snapshot_rows', help="Max number of snapshots to display on page", type=int, default=None)
def set_defaults(**kwargs):
    cli_client.set_default_variables(**kwargs)
    cli_client.list_default_variables()


if __name__ == "__main__":
    sys.exit(cli())
