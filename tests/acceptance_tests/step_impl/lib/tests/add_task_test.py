from tests.acceptance_tests.step_impl.lib.test_strategy import TestStrategy


class AddTaskTest(TestStrategy):

    def __init__(self, name: str, project: str, label: str, due_date: str):
        super().__init__()
        self.__name = name
        self.__project = project
        self.__label = label
        self.__due_date = due_date

    def execute(self):
        response = self.send_request()
        print(response)

        return True

    def send_request(self) -> dict:
        return self.api.add_task(self.__name, self.__project,
                                 self.__label, self.__due_date)
