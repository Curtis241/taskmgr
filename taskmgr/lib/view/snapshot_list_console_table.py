from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.view.console_table import ConsoleTable


class SnapshotListConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["Due Date", "Count", "Completed", "Incomplete", "Deleted"])
        self.__snapshot_list = list()

    def add_row(self, obj):
        assert type(obj) is Snapshot
        row = self.format_row(obj)
        self.get_table().rows.append(row)
        self.__snapshot_list.append(obj)

    def clear(self):
        self.get_table().clear()
        self.__snapshot_list = list()

    def print(self):
        if len(self.get_table().rows) > 0:
            print(self.get_table())
            return self.__snapshot_list
        else:
            print("No rows to display. Use count command.")

    def format_row(self, obj):
        assert type(obj) is Snapshot
        return [obj.due_date, obj.count, obj.completed, obj.incomplete, obj.deleted]
