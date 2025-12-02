# app/shared/repositories/base.py

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get(self, db, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def list(self, db):
        return db.query(self.model).all()

    def add(self, db, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db, obj):
        db.delete(obj)
        db.commit()

    def save(self, db, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

