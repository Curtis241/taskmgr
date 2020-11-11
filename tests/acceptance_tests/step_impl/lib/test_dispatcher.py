from tests.acceptance_tests.step_impl.lib.test_strategy import TestStrategy


class TestDispatcher:

    def __init__(self, test_strategy: TestStrategy):
        self.__strategy = test_strategy

    def run_test(self) -> bool:
        return self.__strategy.execute()
