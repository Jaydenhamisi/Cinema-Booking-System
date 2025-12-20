# app/contexts/auth/events.py

"""
Domain events emitted by AuthContext.
"""


def user_registered_event(user_id: int, email: str) -> dict:
    return {
        "type": "auth.user_registered",
        "payload": {
            "user_id": user_id,
            "email": email,
        },
    }


def user_logged_in_event(user_id: int, email: str) -> dict:
    return {
        "type": "auth.user_logged_in",
        "payload": {
            "user_id": user_id,
            "email": email,
        },
    }


def user_deactivated_event(user_id: int, reason: str = "admin_action") -> dict:
    return {
        "type": "auth.user_deactivated",
        "payload": {
            "user_id": user_id,
            "reason": reason,
        },
    }