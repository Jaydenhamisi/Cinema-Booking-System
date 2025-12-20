from sqlalchemy.orm import Session
from .models import UserCredential

class UserCredentialRepository:

    def get_user_by_id(self, db: Session, user_id: int):
        return db.get(UserCredential, user_id)
    
    def get_user_by_email(self, db: Session, email: str):
        return (
            db.query(UserCredential)
            .filter(UserCredential.email == email)
            .first()
        )

    def create(self, db: Session, usercredential: UserCredential):
        db.add(usercredential)
        db.commit()
        db.refresh(usercredential)
        return usercredential

    def update(self, db: Session, usercredential: UserCredential):
        db.add(usercredential)
        db.commit()
        db.refresh(usercredential)
        return usercredential