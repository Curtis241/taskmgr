from typing import Optional

from pydantic.main import BaseModel


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
    page: int


class LabelArgs(BaseModel):
    label: str
    export: bool = False
    page: int


class NameArgs(BaseModel):
    name: str
    export: bool = False
    page: int


class DueDateRangeArgs(BaseModel):
    min_date: str
    max_date: str
    export: bool = False
    page: int = 0


class DueDateArgs(BaseModel):
    due_date: str
    export: bool = False
    page: int = 1
