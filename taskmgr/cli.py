import sys

import click

from taskmgr.lib.database.db_manager import DatabaseManager, AuthenticationFailed
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.presenter.file_manager import FileManager
from taskmgr.lib.presenter.task_sync import TaskImporter
from taskmgr.lib.presenter.time_card_sync import TimeCardImporter
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.cli_client import CliClient
from taskmgr.lib.view.client_args import *

try:
    db_manager = DatabaseManager()
    cli_client = CliClient(db_manager, FileManager())
    logger = AppLogger("cli").get_logger()
    variables = CommonVariables()
except AuthenticationFailed:
    exit(-1)

@click.group()
def time_card():
    pass


@time_card.command("add", help="Adds a time card")
@click.argument('time_in', type=str, required=True, metavar='<time_in>')
@click.argument('time_out', type=str, required=True, metavar='<time_out>')
@click.option('--date', '-d', type=str, default="today", metavar='<date>')
def add_time_card(**kwargs):
    cli_client.add_time_card(AddTimeCardArgs.parse_obj(kwargs))

@time_card.command("edit", help="Replaces the time card")
@click.argument('index', type=int, required=True, metavar="<index>")
@click.option('--date', '-d', type=str, default=None, metavar='<date>')
@click.option('--time_in', '-i', type=str, default=None, metavar='<time_in>')
@click.option('--time_out', '-o', type=str, default=None, metavar='<time_out>')
def edit_time_card(**kwargs):
    cli_client.edit_time_card(EditTimeCardArgs.parse_obj(kwargs))

@time_card.command("reset", help="Exports and removes all time cards")
@click.option('--confirm', is_flag=True, required=True, help="Confirms removal")
def clear_time_cards(**kwargs):
    if kwargs.get("confirm"):
        query_result = cli_client.time_cards.get_all()
        cli_client.export_time_cards(query_result.to_list())
        cli_client.clear_time_cards()
    else:
        logger.info("Warning: Must use confirm flag before deleting all time cards")

@time_card.command("delete", help="Soft delete")
@click.argument('indexes', nargs=-1, required=True, type=int)
def delete_time_card(**kwargs):
    cli_client.delete_time_card(DeleteArgs.parse_obj(kwargs))

@time_card.command("undelete", help="Reverse soft delete")
@click.argument('indexes', nargs=-1, required=True, type=int)
def undelete_time_card(**kwargs):
    cli_client.undelete_time_card(UndeleteArgs.parse_obj(kwargs))

@time_card.command("list", help="Lists all time cards")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
@click.option('--all', is_flag=True)
def list_time_cards(**kwargs):
    args = ListArgs.parse_obj(kwargs)
    time_card_list = cli_client.list_all_time_cards(args)
    if args.export:
        cli_client.export_time_cards(time_card_list)


@time_card.command("import", help="Imports time cards from csv file")
@click.option('--path', type=str, required=False, metavar="<path>")
@click.option('--columns', is_flag=True, help="Prints expected import csv columns")
def import_time_cards(**kwargs):
    if kwargs.get("columns"):
        cli_client.print_time_card_import_columns()
    else:
        importer = TimeCardImporter(db_manager.get_time_cards_model())
        cli_client.import_time_cards(importer, kwargs.get("path"))

@time_card.command("today", help="Lists only the time cards that have today's date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def today(**kwargs):
    time_card_list = cli_client.filter_time_cards_by_today()
    if kwargs.get("export"):
        cli_client.export_time_cards(time_card_list)


@time_card.group("filter", help="Filters time cards")
def time_card_filter(): pass

@time_card_filter.command("date_range")
@click.option('--min_date', required=True, type=str)
@click.option('--max_date', required=True, type=str)
@click.option('--page', type=int, default=0)
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_time_cards_by_date_range(**kwargs):
    args = DateRangeArgs.parse_obj(kwargs)
    time_card_list = cli_client.filter_time_cards_by_date_range(args)
    if args.export:
        cli_client.export_time_cards(time_card_list)


@time_card_filter.command("date")
@click.argument('date', type=str, required=True, metavar="<date>")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def filter_time_cards_by_date(**kwargs):
    args = DateArgs.parse_obj(kwargs)
    time_card_list = cli_client.filter_time_cards_by_date(args)
    if args.export:
        cli_client.export_time_cards(time_card_list)


@click.group()
def task():
    pass


@task.command("add", help="Appends a task")
@click.argument('name', type=str, required=True, metavar="<name>")
@click.option('--label', '-l', default=variables.default_label, type=str, metavar='<label>')
@click.option('--project', '-p', default=variables.default_project_name, type=str, metavar='<project>')
@click.option('--due_date', '-d', default="today", type=str, metavar='<due_date>')
def add_task(**kwargs):
    cli_client.add_task(AddArgs.parse_obj(kwargs))


@task.command("edit", help="Replaces the task")
@click.argument('index', type=int, required=True, metavar="<index>")
@click.option('--name', '-n', type=str, default=None, metavar='<name>')
@click.option('--label', '-l', type=str, default=None, metavar='<label>')
@click.option('--project', '-p', type=str, default=None, metavar='<project>')
@click.option('--time_spent', '-t', type=float, default=None, metavar='<time_spent>')
@click.option('--due_date', '-d', type=str, default=None, metavar='<due_date>')
def edit_task(**kwargs):
    cli_client.edit_task(EditArgs.parse_obj(kwargs))


@task.command("list", help="Lists all tasks")
@click.option('--export', is_flag=True, help="Outputs to csv file")
@click.option('--page', type=int, default=0)
@click.option('--all', is_flag=True)
def list_tasks(**kwargs):
    args = ListArgs.parse_obj(kwargs)
    task_list = cli_client.list_all_tasks(args)
    if args.export:
        cli_client.export_tasks(task_list)


@task.command("delete", help="Soft delete")
@click.argument('indexes', nargs=-1, required=True, type=int)
def delete_task(**kwargs):
    cli_client.delete_task(DeleteArgs.parse_obj(kwargs))


@task.command("undelete", help="Reverts deleted tasks")
@click.argument('indexes', nargs=-1, required=True, type=int)
def undelete_task(**kwargs):
    cli_client.undelete_task(UndeleteArgs.parse_obj(kwargs))


@task.group("unique", help="Displays unique tasks")
def task_unique(): pass


@task_unique.command("label")
def unique_label_list():
    cli_client.list_labels()


@task_unique.command("project")
def unique_project_list():
    cli_client.list_projects()


@task.group("group", help="Works on groups or orders tasks by type")
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


@task.group("filter", help="Filters tasks")
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


@task.command("today", help="Lists only the tasks that have today's date")
@click.option('--export', is_flag=True, help="Outputs to csv file")
def today(**kwargs):
    task_list = cli_client.filter_tasks_by_today()
    if kwargs.get("export"):
        cli_client.export_tasks(task_list)


@task.group("count", help="Displays task count")
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
@click.argument('project', type=str, required=True, metavar="<project>")
def count_tasks_by_project(**kwargs):
    args = ProjectArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_project(args)


@task_count.command("label")
@click.argument('label', type=str, required=True, metavar="<label>")
def count_tasks_by_label(**kwargs):
    args = LabelArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_label(args)


@task_count.command("name")
@click.argument('name', type=str, required=True, metavar="<name>")
def count_tasks_by_name(**kwargs):
    args = NameArgs.parse_obj(kwargs)
    cli_client.count_tasks_by_name(args)


@task.command("reschedule", help="Moves all tasks from the past to today")
def reschedule():
    cli_client.reschedule_tasks()


@task.command("complete", help="Marks the task as done")
@click.argument('indexes', nargs=-1, required=True, type=int)
@click.option('--time_spent', '-t', type=float, default=0, metavar='<time_spent>')
def complete_task(**kwargs):
    cli_client.complete_task(CompleteArgs.parse_obj(kwargs))


@task.command("incomplete", help="Marks the task as not done")
@click.argument('indexes', nargs=-1, required=True, type=int)
def reset_task(**kwargs):
    cli_client.reset_task(ResetArgs.parse_obj(kwargs))


@task.command("import", help="Imports tasks from csv file")
@click.option('--path', type=str, required=False, metavar="<path>")
@click.option('--columns', is_flag=True, help="Prints expected import csv columns")
def import_tasks(**kwargs):
    if kwargs.get("columns"):
        cli_client.print_task_import_columns()
    else:
        importer = TaskImporter(db_manager.get_tasks_model())
        cli_client.import_tasks(importer, kwargs.get("path"))

@task.command("defaults", help="Sets the default variables")
@click.option('--default_project_name', help="Sets the default project name", type=str, default=None)
@click.option('--default_label', help="Sets the default label", type=str, default=None)
@click.option('--default_name_field_length', help="Sets the default name field length", type=str, default=None)
@click.option('--recurring_month_limit', help="Sets the recurring month limit", type=int, default=None)
@click.option('--redis_port', help="Port for redis database", type=int, default=None)
@click.option('--redis_host', help="IPv4 address for redis database", type=str, default=None)
@click.option('--export_dir', help="Export directory for csv files", type=str, default=None)
@click.option('--max_rows', help="Max number of rows to display on page", type=int, default=None)
def set_defaults(**kwargs):
    cli_client.set_default_variables(**kwargs)
    cli_client.list_default_variables()


if __name__ == "__main__":
    sys.exit(time_card())
