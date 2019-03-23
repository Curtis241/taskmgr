import click
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
              type=click.Choice(DateGenerator("none").get_expressions()))
def add_task(**kwargs):
    print(kwargs)
    print("Adding task: {}".format(kwargs["text"]))
    client.add_task(kwargs["text"], kwargs["label"], kwargs["project"], kwargs["due_date"])


@cli.command("delete")
@click.argument('index', type=int)
def delete_task(**kwargs):
    print("Deleting task {}".format(kwargs["index"]))
    client.delete_task(kwargs["index"])


@cli.command("list")
@click.argument('text', type=click.Choice(['task', 'label', 'project']))
@click.option('--group', '-g', help="Groups tasks by label or project", metavar='<group>',
              type=click.Choice(['label', 'project']))
def list_tasks(**kwargs):
    if kwargs["text"] == "task":
        print("Listing {}:  group {}".format(kwargs["text"], kwargs["group"]))
        client.list_tasks(kwargs["group"])
    if kwargs["text"] == "label":
        print("Listing {}".format(kwargs["text"]))
        client.list_labels()
    if kwargs["text"] == "project":
        print("Listing {}".format(kwargs["text"]))
        client.list_projects()


@cli.command("complete")
@click.argument('index', type=int)
def complete_task(**kwargs):
    print("Task {} completed".format(kwargs["index"]))
    client.complete_task(kwargs["index"])


if __name__ == '__main__':
    cli()
