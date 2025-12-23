from sqlalchemy.orm import Session

from app.core.errors import ValidationError, NotFoundError, ConflictError
from app.shared.services.event_publisher import publish_event

from .schemas import UserProfileUpdate
from .repository import UserProfileRepository
from .models import UserProfile, UserTypeEnum
from .events import (
    profile_created_event,
    profile_updated_event,
    user_type_changed,
    profile_deleted_event
)

class UserProfileService:
    
    def __init__(self):
        self.repo = UserProfileRepository()
    
    def create_profile(self, db: Session, user_id: int, email: str, name: str = None):
        """
        Create user profile (called by event handler on registration).
        """
        # Check if profile already exists
        existing = self.repo.get_by_user_id(db, user_id)
        if existing:
            raise ValueError(f"Profile already exists for user_id {user_id}")
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            email=email,
            name=name,
        )
        
        created_profile = self.repo.create(db, profile)
        
        # Emit event
        event = profile_created_event(created_profile.id, user_id, email)
        publish_event(event["type"], event["payload"])
        
        return created_profile
    

    def get_profile(self, db: Session, user_id: int):
        profile = self.repo.get_by_user_id(db, user_id)
        if profile is None:
            raise NotFoundError("Profile not found")
        
        return profile
    

    def update_profile(self, db: Session, user_id: int, data: UserProfileUpdate):
        profile = self.repo.get_by_user_id(db, user_id)
        if profile is None:
            raise NotFoundError(f"Profile not found for user_id {user_id}")
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)

        updated_profile = self.repo.save(db, profile)

        event = profile_updated_event(updated_profile.id, user_id)
        publish_event(event["type"], event["payload"])

        return updated_profile
    

    def delete_profile(self, db: Session, user_id: int):
        profile = self.repo.get_by_user_id(db, user_id)
        if profile is None:
            raise NotFoundError("Profile not found")
        
        self.repo.delete(db, profile)

        event = profile_deleted_event(user_id)
        publish_event(event["type"], event["payload"])

        return user_id
    

    def admin_update_user_type(self, db: Session, user_id: int, new_type: UserTypeEnum):
        profile = self.repo.get_by_user_id(db, user_id)
        if profile is None:
            raise NotFoundError(f"Profile not found {user_id}")
        
        profile.user_type = new_type

        updated_profile = self.repo.save(db, profile)

        event = user_type_changed(user_id, new_type.value)
        publish_event(event["type"], event["payload"])

        return updated_profile