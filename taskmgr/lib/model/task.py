from taskmgr.lib.model.database import DatabaseObject
from taskmgr.lib.model.due_date import DueDate
from taskmgr.lib.variables import CommonVariables


class Task(DatabaseObject):
    """
    Contains the properties that are needed to represent a task. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """

    def __init__(self, text="default"):
        super().__init__(self.__class__.__name__)
        self.vars = CommonVariables()
        self.__external_id = str()
        self.__text = text
        self.__label = self.vars.default_label
        self.__deleted = False
        self.__priority = 1
        self.__project = self.vars.default_project_name
        self.__date_expression = self.vars.default_date_expression
        self.__due_date = DueDate()

    def get_redis_db_id(self):
        return 0

    @property
    def date_expression(self):
        return self.__date_expression

    @date_expression.setter
    def date_expression(self, expression):
        assert type(expression) is str
        self.__date_expression = expression

    @property
    def due_date(self):
        return self.__due_date

    @due_date.setter
    def due_date(self, due_date):
        self.__due_date = due_date

    def complete(self) -> list:
        self.due_date.completed = True
        return [self.__due_date]

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

    def is_completed(self):
        return self.due_date.completed is True

    def deserialize(self, obj_dict):
        for key, value in obj_dict.items():
            if type(value) is list:
                if key == "due_date" and len(value) == 1:
                    self.due_date = DueDate().from_dict(value[0])
            else:
                setattr(self, key, value)
        return self

    def __eq__(self, other):
        existing = (self.unique_id, self.__text, self.__label, self.__project)
        new = (other.unqiue_id, other.text, self.label, self.project)
        return existing == new

    def __iter__(self):
        yield 'index', self.index
        yield 'external_id', self.external_id
        yield 'text', self.__text
        yield 'label', self.__label
        yield 'deleted', self.__deleted
        yield 'priority', self.__priority
        yield 'project', self.__project
        yield 'date_expression', self.__date_expression
        yield 'due_date', [self.__due_date.to_dict()]
        yield 'unique_id', self.unique_id
        yield 'last_updated', self.last_updated




