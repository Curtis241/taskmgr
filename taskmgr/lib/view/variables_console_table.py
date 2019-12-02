from taskmgr.lib.view.console_table import ConsoleTable


class VariablesConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["Name", "Value"])
        self.__variables_list = list()

    def add_row(self, obj):
        assert type(obj) is list
        self.get_table().append_row(obj)
        self.__variables_list.append(obj)

    def clear(self):
        self.get_table().clear()
        self.__variables_list = list()

    def print(self):
        if len(self.get_table()) > 0:
            print(self.get_table())
            return self.__variables_list

    def format_row(self, obj): pass