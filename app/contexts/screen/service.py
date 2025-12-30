# app/contexts/screen/service.py
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.errors import NotFoundError, ConflictError, ValidationError
from app.shared.services.event_publisher import publish_event_async

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


class ScreenService:
    """Service for Screen and SeatLayout business logic."""
    
    def __init__(self):
        self.screen_repo = ScreenRepository()
        self.layout_repo = SeatLayoutRepository()
    
    # =====================================================================
    # SCREEN OPERATIONS
    # =====================================================================
    
    async def create_screen(
        self, 
        db: Session, 
        data: ScreenCreate, 
        user_id: int = None
    ) -> Screen:
        """Create a new screen."""
        # Validate unique name
        name_conflict = self.screen_repo.get_by_name(db, data.name)
        if name_conflict:
            raise ConflictError(
                "Screen name already exists",
                context={"screen_name": data.name},
            )

        # Validate layout exists
        layout = self.layout_repo.get_by_id(db, data.seat_layout_id)
        if not layout:
            raise NotFoundError(
                "Seat layout not found",
                context={"seat_layout_id": data.seat_layout_id},
            )

        # Validate capacity
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

        # Create screen
        screen = Screen(
            name=data.name,
            capacity=data.capacity,
            seat_layout_id=data.seat_layout_id,
        )

        screen = self.screen_repo.create(db, screen)

        # Emit event
        event = screen_created_event(screen.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return screen

    async def update_screen(
        self, 
        db: Session, 
        screen_id: int, 
        data: ScreenUpdate, 
        user_id: int = None
    ) -> Screen:
        """Update an existing screen."""
        screen = self.screen_repo.get_by_id(db, screen_id)
        if not screen:
            raise NotFoundError("Screen not found", context={"screen_id": screen_id})

        payload = data.model_dump(exclude_unset=True)

        # Validate unique name if changing
        if "name" in payload:
            conflict = self.screen_repo.get_by_name(db, payload["name"])
            if conflict and conflict.id != screen_id:
                raise ConflictError(
                    "Screen name already exists",
                    context={"screen_id": screen_id, "name": payload["name"]},
                )

        # Validate new layout if changing
        new_layout_id = payload.get("seat_layout_id", screen.seat_layout_id)
        new_layout = self.layout_repo.get_by_id(db, new_layout_id)
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

        # Update fields
        for field, value in payload.items():
            setattr(screen, field, value)

        screen = self.screen_repo.save(db, screen)

        # Emit event
        event = screen_updated_event(screen.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return screen

    async def delete_screen(
        self, 
        db: Session, 
        screen_id: int, 
        user_id: int = None
    ) -> None:
        """Delete a screen."""
        screen = self.screen_repo.get_by_id(db, screen_id)
        if not screen:
            raise NotFoundError("Screen not found", context={"screen_id": screen_id})

        self.screen_repo.delete(db, screen)

        # Emit event
        event = screen_deleted_event(screen_id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

    def list_screens(self, db: Session):
        """List all screens (read operation, stays sync)."""
        return self.screen_repo.list_all(db)

    def get_screen(self, db: Session, screen_id: int):
        """Get screen by ID (read operation, stays sync)."""
        screen = self.screen_repo.get_by_id(db, screen_id)
        if not screen:
            raise NotFoundError("Screen not found", context={"screen_id": screen_id})
        return screen

    # =====================================================================
    # LAYOUT OPERATIONS
    # =====================================================================

    async def create_layout(
        self, 
        db: Session, 
        data: SeatLayoutCreate, 
        user_id: int = None
    ) -> SeatLayout:
        """Create a new seat layout."""
        # Validate unique name
        existing = self.layout_repo.get_by_name(db, data.name)
        if existing:
            raise ConflictError(
                message="Layout name must be unique",
                context={"layout_name": data.name},
            )

        # Validate dimensions
        if data.rows <= 0 or data.seats_per_row <= 0:
            raise ValidationError(
                "Invalid layout dimensions; rows and seats_per_row must be > 0",
                context={"rows": data.rows, "seats_per_row": data.seats_per_row},
            )

        # Create layout
        layout = SeatLayout(
            name=data.name,
            rows=data.rows,
            seats_per_row=data.seats_per_row,
            grid=data.grid,
        )

        layout = self.layout_repo.create(db, layout)

        # Emit event
        event = layout_created_event(layout.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return layout

    async def update_layout(
        self, 
        db: Session, 
        layout_id: int, 
        data: SeatLayoutUpdate, 
        user_id: int = None
    ) -> SeatLayout:
        """Update an existing layout."""
        layout = self.layout_repo.get_by_id(db, layout_id)
        if not layout:
            raise NotFoundError("Layout not found", context={"layout_id": layout_id})

        payload = data.model_dump(exclude_unset=True)

        # Name uniqueness check
        if "name" in payload:
            existing = self.layout_repo.get_by_name(db, payload["name"])
            if existing and existing.id != layout_id:
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

        # Update fields
        for field, value in payload.items():
            setattr(layout, field, value)

        layout = self.layout_repo.save(db, layout)

        # Emit event
        event = layout_updated_event(layout.id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

        return layout

    async def delete_layout(
        self, 
        db: Session, 
        layout_id: int, 
        user_id: int = None
    ) -> None:
        """Delete a layout."""
        layout = self.layout_repo.get_by_id(db, layout_id)
        if not layout:
            raise NotFoundError("Layout not found", context={"layout_id": layout_id})

        # Check if any screens use this layout
        screens_using = self.screen_repo.count_screens_using_layout(db, layout_id)

        if screens_using > 0:
            raise ValidationError(
                "Cannot delete layout; screens depend on it",
                context={"layout_id": layout_id, "screens_using": screens_using},
            )

        self.layout_repo.delete(db, layout)

        # Emit event
        event = layout_deleted_event(layout_id, user_id=user_id)
        await publish_event_async(event["type"], event["payload"])

    def list_layouts(self, db: Session):
        """List all layouts (read operation, stays sync)."""
        return self.layout_repo.list_all(db)

    def get_layout(self, db: Session, layout_id: int):
        """Get layout by ID (read operation, stays sync)."""
        layout = self.layout_repo.get_by_id(db, layout_id)
        if not layout:
            raise NotFoundError("Layout not found", context={"layout_id": layout_id})
        return layout