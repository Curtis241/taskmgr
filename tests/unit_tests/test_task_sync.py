import unittest

from taskmgr.lib.presenter.gtasks_api import GTask
from taskmgr.lib.model.task import Task
from taskmgr.lib.presenter.task_sync import ExportAction, ImportAction


class TestTaskSync(unittest.TestCase):

    def setUp(self) -> None: pass

    def tearDown(self) -> None: pass

    def test_export_action_can_insert(self):
        local_task = GTask()
        local_task.title = "Task1"
        local_task.deleted = False

        action = ExportAction(local_task, None)
        self.assertTrue(action.can_insert())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_delete())

    def test_export_action_can_update_when_title_matches(self):
        local_task = GTask()
        local_task.title = "Task1"
        local_task.id = "100"
        local_task.notes = "home"
        local_task.deleted = False

        remote_task = GTask()
        remote_task.title = "Task1"
        remote_task.id = "100"

        action = ExportAction(local_task, remote_task)
        self.assertTrue(action.can_update())
        self.assertFalse(action.can_insert())
        self.assertFalse(action.can_delete())

    def test_export_action_can_update_when_tile_changes(self):
        local_task = GTask()
        local_task.title = "Task2"
        local_task.id = "100"
        local_task.notes = "home"
        local_task.deleted = False

        remote_task = GTask()
        remote_task.title = "Task1"
        remote_task.id = "100"

        action = ExportAction(local_task, remote_task)
        self.assertTrue(action.can_update())
        self.assertFalse(action.can_insert())
        self.assertFalse(action.can_delete())

    def test_export_action_can_delete(self):
        local_task = GTask()
        local_task.title = "Task1"
        local_task.deleted = True
        local_task.id = "100"

        remote_task = GTask()
        remote_task.title = "Task1"
        remote_task.deleted = False
        remote_task.id = "100"

        action = ExportAction(local_task, remote_task)
        self.assertTrue(action.can_delete())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_insert())

    def test_export_action_skip(self):
        local_task = GTask()
        local_task.title = "Task1"

        remote_task = GTask()
        remote_task.title = "Task1"

        action = ExportAction(local_task, remote_task)
        self.assertFalse(action.can_delete())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_insert())

    def test_import_action_can_insert(self):
        action = ImportAction(None, Task("Task1"))
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

        action = ImportAction(local_task, remote_task)
        self.assertTrue(action.can_delete())
        self.assertFalse(action.can_update())
        self.assertFalse(action.can_insert())
