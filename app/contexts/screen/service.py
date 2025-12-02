# app/contexts/screen/service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.core.errors import NotFoundError, ConflictError, ValidationError
from app.shared.services.event_publisher import publish_event

from .models import Screen, SeatLayout
from .schemas import (
    ScreenCreate,
    ScreenUpdate,
    SeatLayoutCreate,
    SeatLayoutUpdate,
)
from .events import (
    screen_created_event,
    screen_updated_event,
    screen_deleted_event,
    layout_created_event,
    layout_updated_event,
    layout_deleted_event,
)

from .repository import ScreenRepository, SeatLayoutRepository


screen_repo = ScreenRepository()
layout_repo = SeatLayoutRepository()


# =====================================================================
# SEAT LAYOUT SERVICE (Repository-Based)
# =====================================================================

def create_layout(db: Session, data: SeatLayoutCreate) -> SeatLayout:
    existing = layout_repo.get_by_name(db, data.name) if hasattr(layout_repo, "get_by_name") else \
        db.scalar(select(SeatLayout).where(SeatLayout.name == data.name))

    if existing:
        raise ConflictError(
            message="Layout name must be unique",
            context={"layout_name": data.name},
        )

    if data.rows <= 0 or data.seats_per_row <= 0:
        raise ValidationError(
            "Invalid layout dimensions; rows and seats_per_row must be > 0",
            context={"rows": data.rows, "seats_per_row": data.seats_per_row},
        )

    layout = SeatLayout(
        name=data.name,
        rows=data.rows,
        seats_per_row=data.seats_per_row,
        grid=data.grid,
    )

    layout_repo.add(db, layout)

    event = layout_created_event(layout.id)
    publish_event(event["type"], event["payload"])

    return layout


def update_layout(db: Session, layout_id: int, data: SeatLayoutUpdate) -> SeatLayout:
    layout = layout_repo.get(db, layout_id)
    if not layout:
        raise NotFoundError("Layout not found", context={"layout_id": layout_id})

    payload = data.model_dump(exclude_unset=True)

    # Name uniqueness check
    if "name" in payload:
        existing = db.scalar(
            select(SeatLayout).where(
                SeatLayout.name == payload["name"],
                SeatLayout.id != layout_id,
            )
        )
        if existing:
            raise ConflictError(
                "Another layout already has this name",
                context={"layout_id": layout_id, "name": payload["name"]},
            )

    # Dimension invariants
    if "rows" in payload and payload["rows"] <= 0:
        raise ValidationError("rows must be > 0", context={"rows": payload["rows"]})

    if "seats_per_row" in payload and payload["seats_per_row"] <= 0:
        raise ValidationError(
            "seats_per_row must be > 0",
            context={"seats_per_row": payload["seats_per_row"]},
        )

    for field, value in payload.items():
        setattr(layout, field, value)

    layout_repo.save(db, layout)

    event = layout_updated_event(layout.id)
    publish_event(event["type"], event["payload"])

    return layout


def delete_layout(db: Session, layout_id: int) -> None:
    layout = layout_repo.get(db, layout_id)
    if not layout:
        raise NotFoundError("Layout not found", context={"layout_id": layout_id})

    screens_using = db.scalar(
        select(func.count())
        .select_from(Screen)
        .where(Screen.seat_layout_id == layout_id)
    )

    if screens_using and screens_using > 0:
        raise ValidationError(
            "Cannot delete layout; screens depend on it",
            context={"layout_id": layout_id, "screens_using": screens_using},
        )

    layout_repo.delete(db, layout)

    event = layout_deleted_event(layout_id)
    publish_event(event["type"], event["payload"])


def list_layouts(db: Session):
    return layout_repo.list(db)


def get_layout(db: Session, layout_id: int):
    layout = layout_repo.get(db, layout_id)
    if not layout:
        raise NotFoundError("Layout not found", context={"layout_id": layout_id})
    return layout


# =====================================================================
# SCREEN SERVICE (Repository-Based)
# =====================================================================

def create_screen(db: Session, data: ScreenCreate) -> Screen:
    # Screen name must be unique
    name_conflict = screen_repo.get_by_name(db, data.name)
    if name_conflict:
        raise ConflictError(
            "Screen name already exists",
            context={"screen_name": data.name},
        )

    layout = layout_repo.get(db, data.seat_layout_id)
    if not layout:
        raise NotFoundError(
            "Seat layout not found",
            context={"seat_layout_id": data.seat_layout_id},
        )

    if data.capacity <= 0:
        raise ValidationError(
            "Capacity must be > 0",
            context={"capacity": data.capacity},
        )

    layout_capacity = layout.rows * layout.seats_per_row
    if data.capacity > layout_capacity:
        raise ValidationError(
            f"Capacity exceeds layout capacity ({layout_capacity})",
            context={"capacity": data.capacity, "layout_capacity": layout_capacity},
        )

    screen = Screen(
        name=data.name,
        capacity=data.capacity,
        seat_layout_id=data.seat_layout_id,
    )

    screen_repo.add(db, screen)

    event = screen_created_event(screen.id)
    publish_event(event["type"], event["payload"])

    return screen


def update_screen(db: Session, screen_id: int, data: ScreenUpdate) -> Screen:
    screen = screen_repo.get(db, screen_id)
    if not screen:
        raise NotFoundError("Screen not found", context={"screen_id": screen_id})

    payload = data.model_dump(exclude_unset=True)

    # Validate unique name
    if "name" in payload:
        conflict = screen_repo.get_by_name(db, payload["name"])
        if conflict and conflict.id != screen_id:
            raise ConflictError(
                "Screen name already exists",
                context={"screen_id": screen_id, "name": payload["name"]},
            )

    # Validate new layout
    new_layout_id = payload.get("seat_layout_id", screen.seat_layout_id)
    new_layout = layout_repo.get(db, new_layout_id)
    if not new_layout:
        raise NotFoundError(
            "Seat layout not found",
            context={"seat_layout_id": new_layout_id},
        )

    # Validate capacity
    new_capacity = payload.get("capacity", screen.capacity)
    if new_capacity <= 0:
        raise ValidationError("Capacity must be > 0", context={"capacity": new_capacity})

    layout_capacity = new_layout.rows * new_layout.seats_per_row
    if new_capacity > layout_capacity:
        raise ValidationError(
            f"Capacity exceeds layout capacity ({layout_capacity})",
            context={"capacity": new_capacity, "layout_capacity": layout_capacity},
        )

    for field, value in payload.items():
        setattr(screen, field, value)

    screen_repo.save(db, screen)

    event = screen_updated_event(screen.id)
    publish_event(event["type"], event["payload"])

    return screen


def delete_screen(db: Session, screen_id: int) -> None:
    screen = screen_repo.get(db, screen_id)
    if not screen:
        raise NotFoundError("Screen not found", context={"screen_id": screen_id})

    screen_repo.delete(db, screen)

    event = screen_deleted_event(screen_id)
    publish_event(event["type"], event["payload"])


def list_screens(db: Session):
    return screen_repo.list(db)


def get_screen(db: Session, screen_id: int):
    screen = screen_repo.get(db, screen_id)
    if not screen:
        raise NotFoundError("Screen not found", context={"screen_id": screen_id})
    return screen

