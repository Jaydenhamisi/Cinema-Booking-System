# app/contexts/screen/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.contexts.auth.dependencies import get_current_user
from .schemas import (
    ScreenCreate,
    ScreenUpdate,
    ScreenRead,
    SeatLayoutCreate,
    SeatLayoutUpdate,
    SeatLayoutRead,
)
from .service import ScreenService

router = APIRouter(
    prefix="/screen",
    tags=["screens"],
)

# Create service instance
screen_service = ScreenService()

# -----------------------------------------------------------
# SCREEN ROUTES
# -----------------------------------------------------------

@router.post(
    "/screens",
    response_model=ScreenRead,
    status_code=status.HTTP_201_CREATED,
)
async def screen_create(
    payload: ScreenCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await screen_service.create_screen(db, payload, user_id=current_user.id)


@router.get(
    "/screens",
    response_model=list[ScreenRead],
)
def list_screens_route(db: Session = Depends(get_db)):
    return screen_service.list_screens(db)


@router.get(
    "/screens/{screen_id}",
    response_model=ScreenRead,
)
def get_screen_route(screen_id: int, db: Session = Depends(get_db)):
    return screen_service.get_screen(db, screen_id)


@router.put(
    "/screens/{screen_id}",
    response_model=ScreenRead,
)
async def screen_update_route(
    screen_id: int,
    payload: ScreenUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await screen_service.update_screen(db, screen_id, payload, user_id=current_user.id)


@router.delete(
    "/screens/{screen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def screen_delete_route(
    screen_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    await screen_service.delete_screen(db, screen_id, user_id=current_user.id)
    return None


# -----------------------------------------------------------
# LAYOUT ROUTES
# -----------------------------------------------------------

@router.post(
    "/layouts",
    response_model=SeatLayoutRead,
    status_code=status.HTTP_201_CREATED,
)
async def layout_create(
    payload: SeatLayoutCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await screen_service.create_layout(db, payload, user_id=current_user.id)


@router.get(
    "/layouts",
    response_model=list[SeatLayoutRead],
)
def list_layouts_route(db: Session = Depends(get_db)):
    return screen_service.list_layouts(db)


@router.get(
    "/layouts/{layout_id}",
    response_model=SeatLayoutRead,
)
def get_layout_route(layout_id: int, db: Session = Depends(get_db)):
    return screen_service.get_layout(db, layout_id)


@router.put(
    "/layouts/{layout_id}",
    response_model=SeatLayoutRead,
)
async def layout_update_route(
    layout_id: int,
    payload: SeatLayoutUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await screen_service.update_layout(db, layout_id, payload, user_id=current_user.id)


@router.delete(
    "/layouts/{layout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def layout_delete_route(
    layout_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    await screen_service.delete_layout(db, layout_id, user_id=current_user.id)
    return None