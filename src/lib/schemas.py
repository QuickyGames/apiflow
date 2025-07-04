from typing import Any, List, Union
import peewee
from pydantic import BaseModel
from pydantic.utils import GetterDict

class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    api_token: str | None = None
from datetime import datetime

class User(UserBase):
    id: int
    date_created: datetime
    date_modified: datetime
    api_token: str
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class JobBase(BaseModel):
    name: str
    status: str

class JobCreate(JobBase):
    runs: int
    owner_id: int

class Job(JobBase):
    id: int
    date_created: datetime
    date_modified: datetime
    runs: int
    owner_id: int
    results: Union[str, None] = None
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class WorkflowBase(BaseModel):
    name: str

class WorkflowCreate(WorkflowBase):
    content: str

class Workflow(WorkflowBase):
    id: int
    date_created: datetime
    date_modified: datetime
    runs: int
    owner_id: int
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class NodeBase(BaseModel):
    name: str

class NodeCreate(NodeBase):
    content: str

class Node(NodeBase):
    id: int
    date_created: datetime
    date_modified: datetime
    owner_id: int
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict
