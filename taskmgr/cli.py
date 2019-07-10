import click
import sys
from taskmgr.lib.client_lib import CliClient, SyncClient
from taskmgr.lib.database import FileDatabase
from taskmgr.lib.date_generator import DateGenerator
from taskmgr.lib.google_tasks_api import GoogleTasksService
from taskmgr.lib.logger import AppLogger
from taskmgr.lib.variables import CommonVariables

cli_client = CliClient(FileDatabase())
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
    date_expression = kwargs["due_date"]
    if DateGenerator().validate_input(date_expression):
        cli_client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])
        cli_client.group_tasks()
    else:
        logger.info(f"Provided due date {date_expression} is invalid")


@cli.command("edit")
@click.argument('key', type=str)
@click.option('--text', '-t', help="text for task", default=None, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=None, type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=None, type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default=CommonVariables.default_date_expression,
              type=str, metavar='<due_date>')
def edit_task(**kwargs):
    date_expression = kwargs["due_date"]
    if DateGenerator().validate_input(date_expression) is False:
        logger.info(f"Provided due date {date_expression} is invalid")
        exit(-1)

    cli_client.edit_task(**kwargs)
    cli_client.group_tasks()


@cli.command("delete")
@click.argument('key', type=str)
def delete_task(**kwargs):
    cli_client.delete_task(kwargs["key"])
    cli_client.group_tasks()


@cli.command("list")
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    cli_client.group_tasks(kwargs["group"])


@cli.command("show")
@click.option('--filter', '-f', help="Filter tasks by complete status", metavar='<filter>',
              type=click.Choice(['incomplete', 'complete']))
def show_tasks(**kwargs):
    cli_client.filter_tasks(kwargs["filter"])


@cli.command("today")
def today():
    cli_client.filter_tasks("due_date")


@cli.command("reschedule")
def reschedule():
    cli_client.reschedule_tasks()
    cli_client.group_tasks()


@cli.command("complete")
@click.argument('key', type=str)
def complete_task(**kwargs):
    cli_client.complete_task(kwargs["key"])
    cli_client.group_tasks()


@cli.command("sync")
def sync():
    sync_client = SyncClient(GoogleTasksService(), FileDatabase())
    sync_client.sync()


if __name__ == "__main__":
    sys.exit(cli())
