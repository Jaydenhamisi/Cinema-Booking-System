# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.base import Base  # Import Base from separate file

# -----------------------------
# Database Engine
# -----------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
    future=True,
)

# -----------------------------
# Session factory
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# -----------------------------
# Dependency for FastAPI routes
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import all models so SQLAlchemy knows about them
from app.contexts.auth.models import UserCredential
from app.contexts.user.models import UserProfile  
from app.contexts.movie.models import Movie
from app.contexts.screen.models import Screen, SeatLayout
from app.contexts.reservation.models import Reservation  
from app.contexts.showtime.models import Showtime         
from app.contexts.seat_availability.models import SeatLock
from app.contexts.order.models import Order
from app.contexts.pricing.models import PriceModifier  
from app.contexts.payment.models import PaymentAttempt  
from app.contexts.refund.models import RefundRequest
from app.contexts.audit.models import AuditLogEntry