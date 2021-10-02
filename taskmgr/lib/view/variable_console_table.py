from taskmgr.lib.view.console_table import ConsoleTable


class VariableConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["Name", "Value"])
        self.__variables_list = list()

    def add_row(self, obj):
        assert type(obj) is list
        self.get_table().rows.append(obj)
        self.__variables_list.append(obj)

    def clear(self):
        self.get_table().clear()
        self.__variables_list = list()

    def print(self):
        if len(self.get_table().rows) > 0:
            print(self.get_table())
            return self.__variables_list

    def format_row(self, obj): pass
