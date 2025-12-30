# app/contexts/pricing/events.py

"""
Domain events emitted by PricingContext.
"""


def pricing_snapshot_created_event(order_id: int, snapshot: dict) -> dict:
    return {
        "type": "pricing.snapshot_created",
        "payload": {
            "order_id": order_id,
            "snapshot": snapshot,
        },
    }


def pricing_modifier_created_event(modifier_id: int, user_id: int = None) -> dict:
    return {
        "type": "pricing.modifier_created",
        "payload": {
            "modifier_id": modifier_id,
            "user_id": user_id,
        },
    }


def pricing_modifier_updated_event(modifier_id: int, user_id: int = None) -> dict:
    return {
        "type": "pricing.modifier_updated",
        "payload": {
            "modifier_id": modifier_id,
            "user_id": user_id,
        },
    }


def pricing_modifier_deleted_event(modifier_id: int, user_id: int = None) -> dict:
    return {
        "type": "pricing.modifier_deleted",
        "payload": {
            "modifier_id": modifier_id,
            "user_id": user_id,
        },
    }