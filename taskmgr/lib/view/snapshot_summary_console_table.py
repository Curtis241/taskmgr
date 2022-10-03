from taskmgr.lib.model.snapshot import Snapshot
from taskmgr.lib.view.console_table import ConsoleTable


class SnapshotSummaryConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["Count", "Completed", "Incomplete",
                          "Deleted", "Total Time", "Average Time"])
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
            print("No rows to display.")

    def format_row(self, obj):
        assert type(obj) is Snapshot
        return [obj.task_count, obj.complete_count, obj.incomplete_count,
                obj.delete_count, obj.total_time, obj.average_time]
