from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.event_bus import event_bus

from .service import UserProfileService

profile_service = UserProfileService()


async def on_user_registered(payload: dict):
    db = SessionLocal()
    try:
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id or not email:
            return
        
        await profile_service.create_profile(  # Added await!
            db,
            user_id=user_id,
            email=email,
        )
    finally:
        db.close()


async def on_admin_force_delete(payload: dict):
    db = SessionLocal()
    try:
        user_id = payload.get("user_id")

        if not user_id:
            return
        
        await profile_service.delete_profile(  # Added await!
            db,
            user_id=user_id,
        )
    finally:
        db.close()


event_bus.subscribe("auth.user_registered", on_user_registered)
event_bus.subscribe("admin.user_force_delete", on_admin_force_delete)