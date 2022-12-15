from taskmgr.lib.database.generic_db import QueryResult
from taskmgr.lib.view.client import Client


class ApiClient(Client):

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def display_tasks(self, result: QueryResult):
        page = result.get_page()
        if page.pager_disabled:
            return {"tasks": [dict(task) for task in result.to_list()],
                    "info": {"item_count": result.item_count}}
        else:
            return {"tasks": [dict(task) for task in result.to_list()],
                    "info": {"item_count": result.item_count,
                             "page_number": page.page_number,
                             "page_count": page.page_count}}

    def display_invalid_index_error(self, index: int):
        return {"error": True, "detail": [{"loc": ["param", "index"]}], "msg": f"Provided index {index} is invalid",
                "type": "attribute_error"}

    def display_snapshots(self, result: QueryResult):
        page = result.get_page()
        if page.pager_disabled:
            return {"snapshot": {"list": [dict(snapshot) for snapshot in result.to_list()]},
                    "info": {"item_count": result.item_count}}
        else:
            return {"snapshot": {"list": [dict(snapshot) for snapshot in result.to_list()]},
                    "info": {"item_count": result.item_count,
                             "page_number": page.page_number,
                             "page_count": page.page_count}}

    def display_attribute_error(self, param: str, message: str):
        return {"error": True, "detail": [{"loc": ["param", param]}], "msg": message, "type": "attribute_error"}

