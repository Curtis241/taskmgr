import sys

import click

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import CsvFileImporter
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient
from taskmgr.lib.view.client_args import *

cli_client = CliClient(DatabaseManager(), FileManager())
logger = AppLogger("cli").get_logger()
variables = CommonVariables()


@click.group()
def cli():
    pass


@cli.command("add", help="Appends a task")
@click.argument('name')
@click.option('--label', '-l', default=variables.default_label, type=str, metavar='<label>')
@click.option('--project', '-p', default=variables.default_project_name, type=str, metavar='<project>')
@click.option('--due_date', '-d', default="today", type=str, metavar='<due_date>')
def add_task(**kwargs):
    cli_client.add(AddArgs.parse_obj(kwargs))


@cli.command("edit", help="Replaces the task")
@click.argument('index', type=int)
@click.option('--name', '-n', type=str, default=None, metavar='<name>')
@click.option('--label', '-l', type=str, default=None, metavar='<label>')
@click.option('--project', '-p', type=str, default=None, metavar='<project>')
@click.option('--time_spent', '-t', type=float, default=None, metavar='<time_spent>')
@click.option('--due_date', '-d', type=str, default=None, metavar='<due_date>')
def edit_task(**kwargs):
    cli_client.edit(EditArgs.parse_obj(kwargs))


@cli.command("list", help="Lists all tasks")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
@click.option('--all', is_flag=True)
def list_tasks(**kwargs):
    args = ListArgs.parse_obj(kwargs)
    task_list = cli_client.list_all_tasks(args)
    if args.export:
        cli_client.export_tasks(task_list)


@cli.command("delete", help="Soft delete")
@click.argument('indexes', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete(DeleteArgs.parse_obj(kwargs))


@cli.command("undelete", help="Reverts deleted tasks")
@click.argument('indexes', nargs=-1, required=True, type=int)
def undelete_task(**kwargs):
    cli_client.undelete(UndeleteArgs.parse_obj(kwargs))


@cli.group("unique", help="Displays unique tasks")
def unique(): pass


@unique.command("label")
def unique_label_list():
    cli_client.list_labels()


@unique.command("project")
def unique_project_list():
    cli_client.list_projects()


@cli.group("group", help="Works on groups or orders tasks by type")
def task_group(): pass


@task_group.command("edit")
@click.argument('indexes', nargs=-1, required=True, type=int)
@click.option('--label', '-l', type=str, default=None, metavar='<label>')
@click.option('--project', '-p', type=str, default=None, metavar='<project>')
@click.option('--time_spent', '-t', type=float, default=None, metavar='<time_spent>')
@click.option('--due_date', '-d', type=str, default=None, metavar='<due_date>')
def group_edit(**kwargs):
    cli_client.group_edit(GroupEditArgs.parse_obj(kwargs))


@task_group.command("label")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def group_tasks_by_label(**kwargs):
    task_list = cli_client.group_tasks_by_label()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_group.command("project")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def group_tasks_by_project(**kwargs):
    task_list = cli_client.group_tasks_by_project()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task_group.command("due_date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def group_tasks_by_due_date(**kwargs):
    task_list = cli_client.group_tasks_by_due_date()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@cli.group("filter", help="Filters tasks")
def task_filter(): pass


@task_filter.command("project")
@click.argument('project', type=str, required=True, metavar="<project>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
def filter_tasks_by_project(**kwargs):
    args = ProjectArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_project(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task_filter.command("status")
@click.argument('status', type=click.Choice(['incomplete', 'complete']), required=True, metavar="<status>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
def filter_tasks_by_status(**kwargs):
    args = StatusArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_status(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task_filter.command("name")
@click.argument('name', type=str, required=True, metavar="<name>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
def filter_tasks_by_name(**kwargs):
    args = NameArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_name(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task_filter.command("label")
@click.argument('label', type=str, required=True, metavar="<label>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
def filter_tasks_by_label(**kwargs):
    args = LabelArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_label(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task_filter.command("date_range")
@click.option('--min_date', required=True, type=str)
@click.option('--max_date', required=True, type=str)
@click.option('--page', type=int, default=0)
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_date_range(**kwargs):
    args = DueDateRangeArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_due_date_range(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task_filter.command("date")
@click.argument('due_date', type=str, required=True, metavar="<due_date>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_tasks_by_date(**kwargs):
    args = DueDateArgs.parse_obj(kwargs)
    task_list = cli_client.filter_tasks_by_due_date(args)
    if args.export:
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
@click.option('--page', type=int, default=0)
def count_all_tasks(**kwargs):
    snapshot_list = cli_client.count_all_tasks(kwargs.get("page"))
    if kwargs.get("export"):
        cli_client.export_snapshots(snapshot_list)


@task_count.command("date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.argument('due_date', type=str, required=True, metavar="<due_date>")
def count_tasks_by_date(**kwargs):
    args = DueDateArgs.parse_obj(kwargs)
    snapshot_list = cli_client.count_tasks_by_due_date(args)
    if args.export:
        cli_client.export_snapshots(snapshot_list)


@task_count.command("date_range")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--min_date', required=True, type=str)
@click.option('--max_date', required=True, type=str)
@click.option('--page', type=int, default=1)
def count_tasks_by_date_range(**kwargs):
    args = DueDateRangeArgs.parse_obj(kwargs)
    snapshot_list = cli_client.count_tasks_by_due_date_range(args)
    if args.export:
        cli_client.export_snapshots(snapshot_list)


@task_count.command("project")
@click.option('--page', type=int, default=1)
@click.argument('project', type=str, required=True, metavar="<project>")
def count_tasks_by_project(**kwargs):
    args = ProjectArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_project(args)


@task_count.command("label")
@click.argument('label', type=str, required=True, metavar="<label>")
@click.option('--page', type=int, default=1)
def count_tasks_by_label(**kwargs):
    args = LabelArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_label(args)


@task_count.command("name")
@click.argument('name', type=str, required=True, metavar="<name>")
@click.option('--page', type=int, default=1)
def count_tasks_by_name(**kwargs):
    args = NameArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_name(args)


@cli.command("reschedule", help="Moves all tasks from the past to today")
def reschedule():
    cli_client.reschedule_tasks()


@cli.command("complete", help="Marks the task as done")
@click.argument('indexes', nargs=-1, required=True, type=int)
@click.option('--time_spent', '-t', type=float, default=0, metavar='<time_spent>')
def complete_task(**kwargs):
    cli_client.complete(CompleteArgs.parse_obj(kwargs))


@cli.command("incomplete", help="Marks the task as not done")
@click.argument('indexes', nargs=-1, required=True, type=int)
def reset_task(**kwargs):
    cli_client.reset(ResetArgs.parse_obj(kwargs))


@cli.command("import", help="Imports tasks from csv file")
@click.option('--path', type=str, required=True, metavar="<path>")
def import_tasks(**kwargs):
    mgr = DatabaseManager()
    cli_client.import_tasks(CsvFileImporter(mgr.get_tasks_model()), kwargs.get("path"))


@cli.command("defaults", help="Sets the default variables")
@click.option('--default_project_name', help="Sets the default project name", type=str, default=None)
@click.option('--default_label', help="Sets the default label", type=str, default=None)
@click.option('--default_name_field_length', help="Sets the default name field length", type=str, default=None)
@click.option('--recurring_month_limit', help="Sets the recurring month limit", type=int, default=None)
@click.option('--redis_port', help="Port for redis database", type=int, default=None)
@click.option('--redis_host', help="IPv4 address for redis database", type=str, default=None)
@click.option('--max_rows', help="Max number of rows to display on page", type=int, default=None)
def set_defaults(**kwargs):
    cli_client.set_default_variables(**kwargs)
    cli_client.list_default_variables()


if __name__ == "__main__":
    sys.exit(cli())
