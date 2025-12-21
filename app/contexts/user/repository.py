from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import UserProfile


class UserProfileRepository:

    def create(self, db: Session, user_profile: UserProfile) -> UserProfile:
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        return user_profile
    

    def get_by_id(self, db: Session, profile_id: int):
        return db.get(UserProfile, profile_id)
    

    def get_by_user_id(self, db: Session, user_id: int):
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    

    def save(self, db: Session, user_profile: UserProfile):
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        return user_profile
    

    def delete(self, db: Session, user_profile: UserProfile):
        db.delete(user_profile)
        db.commit()

    
    def list_all(self, db: Session):
        return db.scalars(select(UserProfile)).all()
    

    def get_by_email(self, db: Session, email: str):
        stmt = select(UserProfile).where(UserProfile.email == email)
        return db.scalar(stmt)