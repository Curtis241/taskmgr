from datetime import datetime


class Time:

    def __init__(self, dt: datetime):
        assert type(dt) is datetime
        self.__dt = dt
        self.time = dt.time()
        self.hour = self.time.hour
        self.minute = self.time.minute

    def to_text(self) -> str:
        if self.hour > 9:
            return f"{int(self.hour):02}:{int(self.minute):02}"
        else:
            return f"{int(self.hour)}:{int(self.minute):02}"

    def to_datetime(self):
        return self.__dt

