from colored import fg
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.view.console_table import ConsoleTable


class TimeCardConsoleTable(ConsoleTable):

    def __init__(self):
        super().__init__(["#", "Time In", "Time Out", "Date", "Elapsed", "Total"])
        self.__time_card_list = list()

    def add_row(self, obj):
        assert isinstance(obj, TimeCard)
        row = self.format_row(obj)
        self.get_table().rows.append(row)
        self.__time_card_list.append(obj)

    def clear(self):
        self.get_table().clear()
        self.__time_card_list = list()

    def print(self):
        if len(self.get_table().rows) > 0:
            print(self.get_table())
            return self.__time_card_list
        else:
            print("No rows to display. Use add command.")
            return []

    def format_row(self, time_card):

        if time_card.deleted:
            time_in = fg('red') + str(time_card.time_in)
            time_out = fg('red') + str(time_card.time_out)
            date = fg('red') + str(time_card.date)
            elapsed_time = fg('red') + str(time_card.elapsed_time)
            total = fg('red') + str(time_card.total)
        else:
            time_in = time_card.time_in
            time_out = time_card.time_out
            date = time_card.date
            elapsed_time = time_card.elapsed_time
            total = time_card.total

        return [time_card.index, time_in, time_out, date,
                elapsed_time, total]

