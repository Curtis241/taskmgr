import textwrap
from colored import fg

from taskmgr.lib.model.task import Task
from taskmgr.lib.variables import CommonVariables
from taskmgr.lib.view.console_table import ConsoleTable


class TaskConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["#", "Done", "Text", "Project", "Label", "Due Date"])
        self.__task_list = list()

    def add_row(self, obj):
        assert isinstance(obj, Task)
        row = self.format_row(obj)
        self.get_table().append_row(row)
        self.__task_list.append(obj)

    def print(self):
        """
        Controls the final display to the console.
        :return: task_list
        """
        if len(self.get_table()) > 0:
            print(self.get_table())
            return self.__task_list
        else:
            print("No rows to display. Use add command.")

    def clear(self):
        self.get_table().clear()
        self.__task_list = list()

    def format_row(self, task):
        """
        Prepares the structure of the table, colors the done column based on status, and shortens
        the text when it exceeds the default length.
        :param task:
        :return: list
        """
        assert type(task) is Task
        text = textwrap.shorten(task.text, CommonVariables().default_text_field_length, placeholder="...")

        if task.is_completed():
            completed_text = fg('green') + str(task.due_date.completed)
        else:
            completed_text = fg('blue') + str(task.due_date.completed)

        return [task.index, completed_text, text, task.project, task.label, task.due_date.date_string]
