# -*- coding: utf-8 -*-
import typing
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import db_manager as db, schemas
from backend.app.database.crud import CRUD

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sleep_time = 10

crud = CRUD()

async def reset_db_state():
    db.db._state._state.set(db.db_state_default.copy())
    db.db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        db.db.connect()
        yield
    finally:
        if not db.db.is_closed():
            db.db.close()


@app.post("/users/signup/", response_model=schemas.User, dependencies=[Depends(get_db)], tags=["User"])
async def create_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)


@app.post("/users/login/", response_model=schemas.User, dependencies=[Depends(get_db)], tags=["User"])
async def login(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="User not found")
    return db_user


@app.post("/notes/create/", response_model=schemas.Note, dependencies=[Depends(get_db)], tags=["Note"])
async def create_note(note: schemas.NoteCreate):
    db_note = crud.create_note(note)
    return db_note


@app.post("/notes/done/", response_model=schemas.Note, dependencies=[Depends(get_db)], tags=["Note"])
async def change_note_status(note: schemas.NoteID):
    db_note = crud.reverse_note_status(note.note_id)
    return db_note


@app.get("/notes/{user_id}", response_model=List[schemas.Note], dependencies=[Depends(get_db)], tags=["Note"])
async def read_note(user_id: str):
    return crud.get_user_notes(user_id=int(user_id))