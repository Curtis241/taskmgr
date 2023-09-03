from typing import Optional

from pydantic.main import BaseModel

class EditTimeCardArgs(BaseModel):
    index: int
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    date: Optional[str] = None

class AddTimeCardArgs(BaseModel):
    time_in: str
    time_out: str
    date: str

class AddArgs(BaseModel):
    name: str
    label: str
    project: str
    due_date: str


class EditArgs(BaseModel):
    index: int
    name: Optional[str] = None
    label: Optional[str] = None
    project: Optional[str] = None
    due_date: Optional[str] = None
    time_spent: Optional[float] = None


class GroupEditArgs(BaseModel):
    indexes: tuple
    label: Optional[str] = None
    project: Optional[str] = None
    due_date: Optional[str] = None
    time_spent: Optional[float] = None


class ListArgs(BaseModel):
    all: bool
    export: bool = False
    page: int


class DeleteArgs(BaseModel):
    indexes: tuple


class UndeleteArgs(BaseModel):
    indexes: tuple


class ResetArgs(BaseModel):
    indexes: tuple


class GetArg(BaseModel):
    index: int


class CompleteArgs(BaseModel):
    indexes: tuple
    time_spent: float


class IncompleteArgs(BaseModel):
    indexes: tuple


class StatusArgs(BaseModel):
    status: str
    export: bool = False
    page: int


class ProjectArgs(BaseModel):
    project: str
    export: bool = False
    page: int = 0


class LabelArgs(BaseModel):
    label: str
    export: bool = False
    page: int = 0


class NameArgs(BaseModel):
    name: str
    export: bool = False
    page: int = 0


class DueDateRangeArgs(BaseModel):
    min_date: str
    max_date: str
    export: bool = False
    page: int = 0


class DueDateArgs(BaseModel):
    due_date: str
    export: bool = False
    page: int = 1

class DateRangeArgs(BaseModel):
    min_date: str
    max_date: str
    export: bool = False
    page: int = 0

class DateArgs(BaseModel):
    date: str
    export: bool = False
    page: int = 1