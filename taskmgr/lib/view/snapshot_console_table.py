from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.view.console_table import ConsoleTable


class SnapshotConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["#", "Date", "Count", "Completed", "Incomplete", "Deleted", "Project"])
        self.__project_summary_list = list()

    def add_row(self, obj):
        assert type(obj) is Snapshot
        row = self.format_row(obj)
        self.get_table().append_row(row)
        self.__project_summary_list.append(obj)

    def clear(self):
        self.get_table().clear()
        self.__project_summary_list = list()

    def print(self):
        if len(self.get_table()) > 0:
            print(self.get_table())
            return self.__project_summary_list
        else:
            print("No rows to display. Use count command.")

    def format_row(self, obj):
        assert type(obj) is Snapshot
        return [obj.index, obj.timestamp, obj.count, obj.completed, obj.incomplete, obj.deleted, obj.project]