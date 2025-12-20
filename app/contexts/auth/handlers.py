# app/contexts/auth/handlers.py

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.event_bus import event_bus
from app.contexts.auth.repository import AuthRepository

auth_repo = AuthRepository()


async def on_admin_force_deactivate(payload: dict):
    """
    Handles admin.user_force_deactivate event.
    Sets user's is_active to False.
    """
    user_id = payload.get("user_id")
    
    if not user_id:
        return
    
    db = SessionLocal()
    try:
        user = auth_repo.get_user_by_id(db, user_id)
        
        if user:
            user.is_active = False
            auth_repo.save(db, user)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error deactivating user {user_id}: {e}")
    finally:
        db.close()


# Event subscriptions
event_bus.subscribe("admin.user_force_deactivate", on_admin_force_deactivate)