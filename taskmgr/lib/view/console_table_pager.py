from taskmgr.lib.variables import CommonVariables


class Page:
    def __init__(self, page_num: int = 0, start: int = 0, end: int = 0):
        self.page_number = page_num
        self.start_index = start
        self.end_index = end

    def exists(self) -> bool:
        return self.page_number != 0


class Pager:

    def __init__(self, snapshot_list: list):
        assert type(snapshot_list) is list

        self.__row_limit = CommonVariables().max_snapshot_rows
        self.__page_items = snapshot_list
        self.__item_count = len(self.__page_items)
        self.__page_count = 1
        self.__page_list = list()

    def assemble(self):
        start_index = 1
        end_index = self.__row_limit

        if self.__item_count >= self.__row_limit:
            self.__page_count = int(round(self.__item_count / self.__row_limit))

        for page_number in range(1, self.__page_count+1):
            if page_number == self.__page_count:
                self.__page_list.append(Page(page_number, start_index, self.__item_count))
            else:
                self.__page_list.append(Page(page_number, start_index, end_index))

            start_index += self.__row_limit
            end_index += self.__row_limit

        return self

    def get_page_count(self) -> int:
        return self.__page_count

    def get_page(self, page_number: int) -> Page:
        assert type(page_number) is int
        page_list = [pg for pg in self.__page_list if pg.page_number == page_number]
        if page_list:
            return page_list[0]
        else:
            return Page()

    def get_items(self, pg: Page) -> list:
        assert isinstance(pg, Page)
        if self.__page_items:
            return [snapshot for snapshot in self.__page_items if pg.start_index <= snapshot.index <= pg.end_index]
        else:
            return list()
