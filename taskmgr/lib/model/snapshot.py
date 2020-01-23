from taskmgr.lib.model.database import DatabaseObject


class Snapshot(DatabaseObject):
    """
    Contains properties needed to define a data Snapshot. The DatabaseObject
    contains only the properties that are used to maintain consistent data.
    """

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.__count = 0
        self.__completed = 0
        self.__incomplete = 0
        self.__deleted = 0
        self.__project = "local"
        self.__location = str()

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        self.__project = project

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        self.__location = location

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, count):
        self.__count = count

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, completed):
        self.__completed = completed

    @property
    def incomplete(self):
        return self.__incomplete

    @incomplete.setter
    def incomplete(self, incomplete):
        self.__incomplete = incomplete

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, deleted):
        self.__deleted = deleted

    @property
    def entity_kind(self):
        return self.__class__.__name__

    def deserialize(self, obj_dict):
        for key, value in obj_dict.items():
            setattr(self, key, value)
        return self

    def __iter__(self):
        yield 'index', self.index
        yield 'unique_id', self.unique_id
        yield 'count', self.__count
        yield 'completed', self.__completed
        yield 'incomplete', self.__incomplete
        yield 'deleted', self.__deleted
        yield 'project', self.__project
        yield 'location', self.__location
        yield 'timestamp', self.last_updated
