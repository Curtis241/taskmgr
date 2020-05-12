from datetime import datetime

from taskmgr.lib.model.gtask import GTask
from taskmgr.lib.variables import CommonVariables


class GTaskProject:
    """
    Models the structure of Google Tasks service tasklist object. Detailed description found here:
    https://developers.google.com/tasks/v1/reference/tasks

    Creating an object allows the tasklist structure model to be serialized from the Google Tasks service
    to an object and then converted to a dictionary when __iter__ is called by using dict(object) method.
    """

    def __init__(self):
        self.__kind = "tasks#taskList"
        self.__id = str()
        self.__title = str()

        dt = datetime.now()
        self.__updated = dt.strftime(CommonVariables().rfc3339_date_time_format)
        self.__tasks = list()

    @property
    def kind(self):
        return self.__kind

    @kind.setter
    def kind(self, kind):
        self.__kind = kind

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def tasks(self):
        return self.__tasks

    def append(self, task):
        assert type(task) is GTask
        self.__tasks.append(task)

    def __iter__(self):
        yield 'kind', self.__kind
        yield 'id', self.__id
        yield 'title', self.__title
