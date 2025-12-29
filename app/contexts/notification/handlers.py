from app.core.event_bus import event_bus
from app.core.database import SessionLocal
from app.contexts.user.repository import UserProfileRepository

from .service import (
    send_booking_confirmation,
    send_payment_failure,
    send_refund_issued,
)

profile_repo = UserProfileRepository()


async def on_payment_succeeded(payload: dict):
    # Fetch user email from database
    user_id = payload.get("user_id")
    if not user_id:
        return  # Can't send email without user_id
    
    db = SessionLocal()
    try:
        profile = profile_repo.get_by_user_id(db, user_id)  # ← FIXED!
        if not profile:
            return  # User profile not found
        
        # Add user_email to payload for the email template
        email_payload = {**payload, "user_email": profile.email}
        send_booking_confirmation(email_payload)
    finally:
        db.close()


async def on_payment_failed(payload: dict):
    # Fetch user email from database
    user_id = payload.get("user_id")
    if not user_id:
        return  # Can't send email without user_id
    
    db = SessionLocal()
    try:
        profile = profile_repo.get_by_user_id(db, user_id)  # ← FIXED!
        if not profile:
            return  # User profile not found
        
        # Add user_email to payload for the email template
        email_payload = {**payload, "user_email": profile.email}
        send_payment_failure(email_payload)
    finally:
        db.close()


async def on_refund_issued(payload: dict):
    # Fetch user email from database
    user_id = payload.get("user_id")
    if not user_id:
        return  # Can't send email without user_id
    
    db = SessionLocal()
    try:
        profile = profile_repo.get_by_user_id(db, user_id)  # ← FIXED!
        if not profile:
            return  # User profile not found
        
        # Add user_email to payload for the email template
        email_payload = {**payload, "user_email": profile.email}
        send_refund_issued(email_payload)
    finally:
        db.close()


event_bus.subscribe("payment.succeeded", on_payment_succeeded)
event_bus.subscribe("payment.failed", on_payment_failed)
event_bus.subscribe("refund.issued", on_refund_issued)