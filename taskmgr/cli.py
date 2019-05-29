import click
import sys
from taskmgr.lib.client_lib import CliClient
from taskmgr.lib.date_generator import DateGenerator

client = CliClient()


@click.group()
def cli():
    pass


@cli.command("add")
@click.argument('text')
@click.option('--label', '-l', help="label for task", default="all", type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default="inbox", type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default="today",
              type=click.Choice(DateGenerator().get_expressions()))
def add_task(**kwargs):
    client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])
    client.group_tasks()


@cli.command("edit")
@click.argument('index', type=int)
@click.option('--text', '-t', help="text for task", default=None, type=str, metavar='<text>')
@click.option('--label', '-l', help="label for task", default=None, type=str, metavar='<label>')
@click.option('--project', '-p', help="project for task", default=None, type=str, metavar='<project>')
@click.option('--due-date', '-d', help="due date for task", default=None,
              type=click.Choice(DateGenerator().get_expressions()))
def edit_task(**kwargs):
    client.edit_task(**kwargs)
    client.group_tasks()


@cli.command("delete")
@click.argument('index', type=int)
def delete_task(**kwargs):
    client.delete_task(kwargs["index"])
    client.group_tasks()


@cli.command("list")
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    client.group_tasks(kwargs["group"])


@cli.command("today")
def today():
    client.filter_tasks("due_date")


@cli.command("reschedule")
def reschedule():
    client.reschedule_tasks()
    client.group_tasks()


@cli.command("complete")
@click.argument('index', type=int)
def complete_task(**kwargs):
    client.complete_task(kwargs["index"])
    client.group_tasks()


if __name__ == "__main__":
    sys.exit(cli())