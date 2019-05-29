from taskmgr.lib.database import FileDatabase


class FileTestDatabase(FileDatabase):

    def __init__(self):
        super().__init__()
        self.remove()

    def get_db_path(self):
        return self.make_db_path("test_tasks_db")
