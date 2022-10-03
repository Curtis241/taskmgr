import unittest

from taskmgr.lib.database.generic_db import QueryParams


class TestQueryParams(unittest.TestCase):

    def test_single_string_param(self):
        query = QueryParams("label", "my_label").build()
        self.assertEqual(query.query_string(), '@label:my_label')

    def test_single_bool_param(self):
        query = QueryParams("completed", True).build()
        self.assertEqual(query.query_string(), '@completed:True')

    def test_single_int_param(self):
        query = QueryParams("due_date_timestamp", 129345678).build()
        self.assertEqual(query.query_string(), '@due_date_timestamp:[129345678 129345678]')

    def test_double_int_param(self):
        query = QueryParams("due_date_timestamp", 129345678, 2324568989).build()
        self.assertEqual(query.query_string(), '@due_date_timestamp:[129345678 2324568989]')
