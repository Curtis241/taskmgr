from abc import abstractmethod

from beautifultable import BeautifulTable, ALIGN_LEFT, STYLE_BOX


class ConsoleTable:

    def __init__(self, column_headers):
        assert type(column_headers) is list
        self.__table = BeautifulTable(default_alignment=ALIGN_LEFT, max_width=200)
        self.__table.set_style(STYLE_BOX)
        self.__table.column_headers = column_headers

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