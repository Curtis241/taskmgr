

class DueDate(object):
    """The DueDate object was created to support reoccurring tasks. When there are many dates each
    date can be marked as completed."""

    def __init__(self):
        self.__completed = False
        self.__date_string = str()

    @property
    def completed(self):
        return self.__completed

    @completed.setter
    def completed(self, is_completed):
        assert type(is_completed) is bool
        self.__completed = is_completed

    @property
    def date_string(self):
        return self.__date_string

    @date_string.setter
    def date_string(self, date_string):
        """
        Store a datetime object converted to a date string using a formatter.
        See the CommonVariables.date_format formatter
        :param date_string:
        :return:
        """
        assert type(date_string) is str
        self.__date_string = date_string

    def to_dict(self):
        """
        Converts object to dict
        :return:  dict
        """
        return {"date_string": self.__date_string, "completed": self.__completed}

    def from_dict(self, due_date_dict):
        """
        Converts dict to object
        :param due_date_dict: DueDate dict
        :return: DueDate object
        """
        if "date_string" in due_date_dict:
            self.__date_string = due_date_dict["date_string"]

        if "completed" in due_date_dict:
            self.__completed = due_date_dict["completed"]

        return self

