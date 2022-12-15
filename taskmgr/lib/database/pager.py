from typing import Optional

from taskmgr.lib.logger import AppLogger


class Page:
    def __init__(self, page_num: int = 0, offset: int = 0,
                 row_limit: int = 0, page_count: int = 0):
        self.page_number = page_num
        self.page_count = page_count
        self.offset = offset
        self.row_limit = row_limit
        self.pager_disabled = False


class Pager:

    logger = AppLogger("pager").get_logger()

    def __init__(self, item_count: int, row_limit: int):
        self.row_limit = row_limit
        self.item_count = item_count
        self.page_count = 1
        self.offset = 0
        self.__page_list = list()
        self.__assemble_pages()

    def __assemble_pages(self):

        # If there are items found using given query
        if self.item_count >= self.row_limit:
            self.page_count = int(round(self.item_count / self.row_limit))

            for page_number in range(1, self.page_count+1):
                page = Page(page_number, self.offset,
                            self.row_limit, self.page_count)
                self.__page_list.append(page)
                self.offset += self.row_limit
        else:
            page = Page(1, self.offset,
                        self.row_limit, self.page_count)
            page.pager_disabled = True
            self.__page_list.append(page)

        return self

    def get_page(self, page_number: int) -> Optional[Page]:
        assert type(page_number) is int
        if page_number == 0:
            page = Page(row_limit=self.item_count)
            page.pager_disabled = True
            return page
        else:
            page_list = [pg for pg in self.__page_list if pg.page_number == page_number]
            if page_list:
                return page_list[0]

