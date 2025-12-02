# app/contexts/screen/router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import (
    ScreenCreate,
    ScreenUpdate,
    ScreenRead,
    SeatLayoutCreate,
    SeatLayoutUpdate,
    SeatLayoutRead,
)
from .service import (
    create_screen,
    update_screen,
    delete_screen,
    get_screen,
    list_screens,
    create_layout,
    update_layout,
    delete_layout,
    get_layout,
    list_layouts,
)

router = APIRouter(
    prefix="/screen",
    tags=["screens"],
)

# -----------------------------------------------------------
# SCREEN ROUTES
# -----------------------------------------------------------


@router.post(
    "/screens",
    response_model=ScreenRead,
    status_code=status.HTTP_201_CREATED,
)
def screen_create(payload: ScreenCreate, db: Session = Depends(get_db)):
    return create_screen(db=db, data=payload)


@router.get(
    "/screens",
    response_model=list[ScreenRead],
)
def list_screens_route(db: Session = Depends(get_db)):
    return list_screens(db=db)


@router.get(
    "/screens/{screen_id}",
    response_model=ScreenRead,
)
def get_screen_route(screen_id: int, db: Session = Depends(get_db)):
    return get_screen(db=db, screen_id=screen_id)


@router.put(
    "/screens/{screen_id}",
    response_model=ScreenRead,
)
def screen_update_route(
    screen_id: int,
    payload: ScreenUpdate,
    db: Session = Depends(get_db),
):
    return update_screen(db=db, screen_id=screen_id, data=payload)


@router.delete(
    "/screens/{screen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def screen_delete_route(screen_id: int, db: Session = Depends(get_db)):
    delete_screen(db=db, screen_id=screen_id)
    return None


# -----------------------------------------------------------
# LAYOUT ROUTES
# -----------------------------------------------------------


@router.post(
    "/layouts",
    response_model=SeatLayoutRead,
    status_code=status.HTTP_201_CREATED,
)
def layout_create(payload: SeatLayoutCreate, db: Session = Depends(get_db)):
    return create_layout(db=db, data=payload)


@router.get(
    "/layouts",
    response_model=list[SeatLayoutRead],
)
def list_layouts_route(db: Session = Depends(get_db)):
    return list_layouts(db=db)


@router.get(
    "/layouts/{layout_id}",
    response_model=SeatLayoutRead,
)
def get_layout_route(layout_id: int, db: Session = Depends(get_db)):
    return get_layout(db=db, layout_id=layout_id)


@router.put(
    "/layouts/{layout_id}",
    response_model=SeatLayoutRead,
)
def layout_update_route(
    layout_id: int,
    payload: SeatLayoutUpdate,
    db: Session = Depends(get_db),
):
    return update_layout(db=db, layout_id=layout_id, data=payload)


@router.delete(
    "/layouts/{layout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def layout_delete_route(layout_id: int, db: Session = Depends(get_db)):
    delete_layout(db=db, layout_id=layout_id)
    return None
