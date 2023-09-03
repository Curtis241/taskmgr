import unittest

from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.sync import ImportActions


class TestTaskSync(unittest.TestCase):

    def setUp(self) -> None: pass

    def tearDown(self) -> None: pass

    def test_import_action_can_insert(self):
        action = ImportActions(None, Task("Task1"))
        self.assertTrue(action.can_insert())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_delete())

    def test_import_action_can_delete(self):

        remote_task = Task("Task1")
        remote_task.external_id = "100"
        remote_task.deleted = True

        local_task = Task("Task1")
        local_task.external_id = "100"
        local_task.deleted = False

        action = ImportActions(local_task, remote_task)
        self.assertTrue(action.can_delete())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_insert())

