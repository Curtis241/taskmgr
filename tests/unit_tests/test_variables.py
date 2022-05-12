import unittest

from taskmgr.lib.variables import CommonVariables


class TestVariables(unittest.TestCase):

    def setUp(self) -> None:
        self.vars = CommonVariables('test_variables.ini')

    def test_dir_variables(self):
        self.assertIsInstance(self.vars.log_dir, str)
        self.assertIsInstance(self.vars.credentials_dir, str)
        self.assertIsInstance(self.vars.resources_dir, str)

    def test_date_time_variables(self):
        self.assertIsInstance(self.vars.date_format, str)
        self.assertIsInstance(self.vars.date_time_format, str)
        self.assertIsInstance(self.vars.time_format, str)
        self.assertIsInstance(self.vars.rfc3339_date_time_format, str)
        self.assertIsInstance(self.vars.file_name_timestamp, str)

    def test_task_variables(self):
        self.assertIsInstance(self.vars.default_label, str)
        self.assertIsInstance(self.vars.default_project_name, str)
        self.assertIsInstance(self.vars.default_name, str)
        self.assertIsInstance(self.vars.recurring_month_limit, int)
        self.assertIsInstance(self.vars.default_name_field_length, int)

    def test_redisdb_variables(self):
        self.assertIsInstance(self.vars.redis_port, int)
        self.assertIsInstance(self.vars.redis_host, str)

    def test_set_variable(self):
        self.vars.default_project_name = "work"
        self.assertTrue(self.vars.default_project_name == "work")

        vars = CommonVariables('test_variables.ini')
        self.assertTrue(vars.default_project_name == "work")

        vars.reset()
        self.assertTrue(len(str(vars.default_project_name)) == 0)

    def test_date_format_validation(self):
        self.assertTrue(self.vars.validate_date_format('2020-01-01'))
        self.assertFalse(self.vars.validate_date_format('2020-01-011'))
        self.assertFalse(self.vars.validate_date_format('20201-01-01'))
        self.assertFalse(self.vars.validate_date_format('01-01-2020'))


if __name__ == '__main__':
    unittest.main()
