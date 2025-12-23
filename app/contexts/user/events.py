"""
Domain events emitted by UserContext
"""

from .models import UserTypeEnum

def profile_created_event(profile_id: int, user_id: int, email: str, name: str = None) -> dict:
    return {
        "type": "user.profile_created",
        "payload": {
            "profile_id": profile_id,
            "user_id": user_id,
            "email": email,
            "name": name,
        },
    }


def profile_updated_event(profile_id: int, user_id: int) -> dict:
    return {
        "type": "user.profile_updated",
        "payload": {
            "profile_id": profile_id,
            "user_id": user_id,
        },
    }


def user_type_changed(user_id: int, new_type: UserTypeEnum) -> dict:
    return {
        "type": "user.user_type_changed",
        "payload": {
            "user_id": user_id,
            "new_type": new_type.value,
        },
    }


def profile_deleted_event(user_id: int) -> dict:
    return {
        "type": "user.profile_deleted",
        "payload": {
            "user_id": user_id
        },
    }
