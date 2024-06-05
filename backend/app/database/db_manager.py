# -*- coding: utf-8 -*-

import os
from contextvars import ContextVar
import peewee as pw
from peewee import SqliteDatabase
from playhouse.cockroachdb import CockroachDatabase
from dotenv import load_dotenv

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())

load_dotenv()

db = CockroachDatabase(os.getenv("COCKROACH_URL"))


class PeeweeConnectionState(pw._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db._state = PeeweeConnectionState()


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    email = pw.CharField()
    password = pw.CharField()


class Note(BaseModel):
    title = pw.CharField()
    content = pw.CharField()
    owner_id = pw.ForeignKeyField(User)
    done = pw.BooleanField()


class Affill(BaseModel):
    user_id = pw.ForeignKeyField(User)
    note_id = pw.ForeignKeyField(Note)


def create_tables():
    with db:
        db.create_tables([User, Note, Affill])


def drop_tables():
    db.drop_tables([User, Note, Affill])


if __name__ == "__main__":
    create_tables()