from datetime import datetime

from taskmgr.lib.variables import CommonVariables


class GTask:
    """
    Models the structure of Google Tasks service task object. Detailed description found here:
    https://developers.google.com/tasks/v1/reference/tasks

    Creating an object allows the task structure model to be serialized from the Google Tasks service
    to an object and then converted to a dictionary when __iter__ is called by using dict(object) method.
    """

    def __init__(self):
        self.__kind = "tasks#task"
        self.__id = str()
        self.__title = str()
        self.__parent = str(0)
        self.__position = str(0)
        self.__notes = str()
        self.__status = 'needsAction'
        self.__updated = self.get_current_date()
        self.__due = str()
        self.__is_completed = False
        self.__completed = str()
        self.__deleted = False
        self.__hidden = False

    def __iter__(self):
        yield 'kind', self.__kind
        yield 'id', self.__id
        yield 'title', self.__title
        yield 'parent', self.__parent
        # yield 'position', self.__position
        yield 'notes', self.__notes
        yield 'status', self.__status
        # yield 'updated', self.__updated

        # if due and completed are included when they are empty
        # service throws 404 error.
        if len(self.__due) > 0:
            yield 'due', self.__due

        if len(self.__completed) > 0:
            yield 'completed', self.__completed

        yield 'deleted', self.__deleted
        yield 'hidden', self.__hidden

    @staticmethod
    def get_current_date():
        dt = datetime.now()
        return dt.strftime(CommonVariables().rfc3339_date_time_format)

    def is_completed(self, completed):
        assert type(completed) is bool
        if completed:
            self.__status = "completed"
            self.__completed = self.get_current_date()

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
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, notes):
        self.__notes = notes

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def updated(self):
        return self.__updated

    @updated.setter
    def updated(self, updated):
        self.__updated = updated

    @property
    def due(self):
        return self.__due

    @due.setter
    def due(self, due):
        self.__due = due

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, completed):
        self.__completed = completed

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, deleted):
        self.__deleted = deleted

    @property
    def hidden(self):
        return self.__hidden

    @hidden.setter
    def hidden(self, hidden):
        self.__hidden = hidden