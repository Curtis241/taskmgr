from abc import abstractmethod

from beautifultable import BeautifulTable, enums


class ConsoleTable:

    def __init__(self, column_headers):
        assert type(column_headers) is list
        self.__table = BeautifulTable(default_alignment=enums.ALIGN_LEFT, maxwidth=200)
        self.__table.set_style(enums.STYLE_BOX)
        self.__table.columns.header = column_headers

    @abstractmethod
    def add_row(self, obj): pass

    @abstractmethod
    def clear(self): pass

    def get_table(self):
        return self.__table

    @abstractmethod
    def print(self): pass

    @abstractmethod
    def format_row(self, obj): pass
