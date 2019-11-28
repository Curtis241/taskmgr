import uuid

from taskmgr.lib.presenter.date_generator import DateGenerator, DueDate
from taskmgr.lib.variables import CommonVariables


class Task(object):

    def __init__(self, text, date_generator=None):
        self.vars = CommonVariables()
        self.__id = uuid.uuid4().hex
        self.__index = int()
        self.__external_id = str()
        self.__text = text
        self.__label = self.vars.default_label
        self.__deleted = False
        self.__priority = 1
        self.__project = self.vars.default_project_name
        self.__last_updated = str()

        if date_generator is None:
            self.date_generator = DateGenerator()
        else:
            self.date_generator = date_generator

        self.__date_expression = self.vars.default_date_expression
        self.__due_dates = [DueDate()]

    @property
    def date_expression(self):
        return self.__date_expression

    @date_expression.setter
    def date_expression(self, expression):
        assert type(expression) is str
        if len(str(expression)) > 0:
            self.__date_expression = expression
            due_dates = self.date_generator.get_due_dates(expression)
            self.__due_dates = due_dates

    @property
    def due_dates(self):
        return self.__due_dates

    @due_dates.setter
    def due_dates(self, due_date_list):
        assert type(due_date_list) is list
        if len(due_date_list) > 1:
            assert type(due_date_list[0]) is DueDate
        self.__due_dates = due_date_list

    def complete(self) -> list:
        if len(self.__due_dates) > 0:
            due_date_list = [due_date for due_date in self.__due_dates if not due_date.completed]
            due_date_list[0].completed = True
            return due_date_list
        return list()

    def is_completed(self) -> bool:
        completed_tasks: int = len(list(filter(lambda d: d.completed is True, self.__due_dates)))
        total_tasks: int = len(self.__due_dates)
        if completed_tasks == 0 and total_tasks == 0:
            return False
        else:
            return completed_tasks == total_tasks

    def get_date_string_list(self) -> list:
        # If there is only 1 due_date then get the last object
        if len(self.due_dates) == 1:
            due_date = self.due_dates[-1]
            return [due_date.date_string, ""]

        elif len(self.due_dates) > 1:
            due_date_list = list(filter(lambda d: d.completed is False, self.due_dates))

            # If there are completed due_dates; then get the first .
            if len(due_date_list) > 0:
                return [due_date_list[0].date_string, due_date_list[-1].date_string]

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        self.__index = int(index)

    @property
    def external_id(self):
        return self.__external_id

    @external_id.setter
    def external_id(self, external_id):
        self.__external_id = external_id

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        if len(str(project)) > 0 and project is not None:
            self.__project = project

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if len(str(text)) > 0 and text is not None:
            self.__text = text

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        if label is not None:
            self.__label = label

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, deleted):
        assert type(deleted) is bool
        self.__deleted = deleted

    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, priority):
        assert type(priority) is int
        self.__priority = priority

    @property
    def last_updated(self):
        return self.__last_updated

    @last_updated.setter
    def last_updated(self, last_updated):
        assert type(last_updated) is str
        self.__last_updated = last_updated

    def __iter__(self):
        yield 'id', self.__id
        yield 'external_id', self.external_id
        yield 'index', self.__index
        yield 'text', self.__text
        yield 'label', self.__label
        yield 'deleted', self.__deleted
        yield 'priority', self.__priority
        yield 'project', self.__project
        yield 'date_expression', self.__date_expression
        yield 'due_dates', [due_date.to_dict() for due_date in self.due_dates]
        yield 'last_updated', self.__last_updated
