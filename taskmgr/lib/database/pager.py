from typing import Optional


class Page:
    def __init__(self, page_num: int = 0, offset: int = 0, row_limit: int = 0):
        self.page_number = page_num
        self.offset = offset
        self.row_limit = row_limit


class Pager:

    def __init__(self, item_count: int, row_limit: int):
        self.row_limit = row_limit
        self.item_count = item_count
        self.page_count = 1
        self.__page_list = list()

    def assemble_pages(self):
        offset = 1

        if self.item_count >= self.row_limit:
            self.page_count = int(round(self.item_count / self.row_limit))

        for page_number in range(1, self.page_count+1):
            self.__page_list.append(Page(page_number, offset, self.row_limit))
            offset += self.row_limit

        return self

    def get_page(self, page_number: int) -> Optional[Page]:
        assert type(page_number) is int
        page_list = [pg for pg in self.__page_list if pg.page_number == page_number]
        if page_list:
            return page_list[0]

