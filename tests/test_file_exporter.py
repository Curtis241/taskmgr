# class TestFileExporter(unittest.TestCase):
#
#     def setUp(self) -> None:
#         self.db = JsonFileDatabase(db_name="test_file_exporter_db")
#
#         self.row1 = TableRow([0, "True", "Task1", "work", "", "2019-01-01", ""])
#         self.row2 = TableRow([1, "False", "Task2", "taskmgr", "bugs", "2019-01-01", ""])
#         self.rows = [self.row1, self.row2]
#
#     def tearDown(self): pass
#
#     def test_save(self):
#         exporter = FileExporter()
#         path = exporter.save(self.rows, "new_path")

