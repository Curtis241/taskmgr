class Task(object):

    def __init__(self, text):
        self.__index = 0
        self.__text = text
        self.__label = "@all"
        self.__completed = False
        self.__deleted = False
        self.__priority = 1
        self.__project = "inbox"
        self.__due_date = list()

    @property
    def due_date(self):
        return self.__due_date

    @due_date.setter
    def due_date(self, due_date):
        self.__due_date = due_date

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        if len(str(project)) > 0:
            self.__project = project

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        self.__index = int(index)

    @property
    def text(self):
        return self.__text

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        assert type(label) is str
        if str(label).startswith("@"):
            self.__label = label
        else:
            if len(str(label)) > 0:
                self.__label = "@{}".format(label)

    @property
    def is_complete(self):
        return self.__completed

    @is_complete.setter
    def is_complete(self, completed):
        assert type(completed) is bool
        self.__completed = completed

    @property
    def delete(self):
        return self.__deleted

    @delete.setter
    def delete(self, deleted):
        assert type(deleted) is bool
        self.__deleted = deleted

    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, priority):
        assert type(priority) is int
        self.__priority = priority

    def __iter__(self):
        yield 'index', self.__index
        yield 'text', self.__text
        yield 'label', self.__label
        yield 'completed', self.__completed
        yield 'deleted', self.__deleted
        yield 'priority', self.__priority
        yield 'project', self.__project
        yield 'due_date', self.__due_date

