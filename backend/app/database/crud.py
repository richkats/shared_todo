from backend.app.database import schemas, db_manager as models
from backend.app.database.db_manager import Affill


# Фасад, который реализует логику работы с базой данных
class CRUD:
    def get_user(self, user_id: int):
        return models.User.filter(models.User.id == user_id).first()


    def get_user_by_email(self, email: str):
        return models.User.filter(models.User.email == email).first()


    def get_user_notes(self, user_id: int):
        notes = []
        # affils = models.Affill.select().where(models.Affill.user_id == user_id)
        query = (models.Affill.select().where(Affill.user_id == user_id))
        for note in query:
            notes.append(note.note_id)
        return list(notes)


    def create_user(self, user: schemas.UserCreate):
        user = models.User(**user.dict())
        user.save()
        return user


    def create_note(self, note: schemas.NoteCreate):
        note = models.Note(**note.dict(), done=False)
        note.save()
        models.Affill.create(user_id=note.owner_id, note_id=note.id)
        return note


    def get_note(self, note_id: int) -> models.Note:
        return models.Note.filter(models.Note.id == note_id).first()


    def add_user_to_note(self, user_id: int, note_id: int):
        return models.Affill.create(user_id=user_id, note_id=note_id)

    def reverse_note_status(self, note_id: int):
        note = self.get_note(note_id)
        q = (note.update({models.Note.done: not note.done}))
        q.execute()
        return note
