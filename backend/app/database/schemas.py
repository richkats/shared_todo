from typing import Any, List, Union
import peewee
from pydantic import BaseModel, validator
from pydantic.utils import GetterDict

from backend.app.database import db_manager


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class NoteBase(BaseModel):
    title: str
    content: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class NoteCreate(NoteBase):
    owner_id: int


class Note(NoteBase):
    id: int
    owner_id: User
    done: bool


class NoteID(BaseModel):
    note_id: int


class Notes(BaseModel):
    notes: List[Note]