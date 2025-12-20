from sqlalchemy.orm import Session
from .models import UserCredential

class AuthRepository:  

    def get_user_by_id(self, db: Session, user_id: int):
        return db.get(UserCredential, user_id)
    
    def get_user_by_email(self, db: Session, email: str):
        return (
            db.query(UserCredential)
            .filter(UserCredential.email == email)
            .first()
        )

    def create_user(self, db: Session, *, email: str, hashed_password: str) -> UserCredential:
        """Helper to create user from email/password"""
        user = UserCredential(
            email=email,
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create(self, db: Session, user_credential: UserCredential):
        """Generic create for UserCredential object"""
        db.add(user_credential)
        db.commit()
        db.refresh(user_credential)
        return user_credential

    def save(self, db: Session, user_credential: UserCredential):
        """Update existing user"""
        db.add(user_credential)
        db.commit()
        db.refresh(user_credential)
        return user_credential