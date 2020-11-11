from getgauge.python import step

from tests.acceptance_tests.step_impl.lib.test_dispatcher import TestDispatcher
from tests.acceptance_tests.step_impl.lib.tests.add_task_test import AddTaskTest


@step("Add <name> project <project> label <label> due_date <due_date>")
def add_task(name, project, label, due_date):
    test = AddTaskTest(name, project, label, due_date)
    assert TestDispatcher(test).run_test()
