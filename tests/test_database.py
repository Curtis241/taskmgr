import unittest

from taskmgr.lib.database import JsonFileDatabase, YamlFileDatabase
from taskmgr.lib.task import Task


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        db_name = "test_database_file_db"
        self.json_db = JsonFileDatabase(db_name)
        self.yaml_db = YamlFileDatabase(db_name)

    def tearDown(self) -> None:
        self.json_db.remove()
        self.yaml_db.remove()

    def test_json_db(self):
        task = Task("test")
        export_list = [dict(task)]
        self.json_db.save(export_list)

        import_list = self.json_db.retrieve()
        self.assertListEqual(export_list, import_list)

    def test_yaml_db(self):
        task = Task("test")
        export_list = [dict(task)]
        self.yaml_db.save(export_list)

        import_list = self.yaml_db.retrieve()
        self.assertListEqual(export_list, import_list)