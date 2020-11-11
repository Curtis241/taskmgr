from abc import abstractmethod

from tests.acceptance_tests.step_impl.lib.taskmgr_api import TaskmgrApi


class TestStrategy:

    def __init__(self):
        self.api = TaskmgrApi()

    @abstractmethod
    def send_request(self) -> dict: pass

    @abstractmethod
    def execute(self) -> bool: pass