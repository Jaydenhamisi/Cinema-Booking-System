# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

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
# Base class for all models
# -----------------------------
Base = declarative_base()

# -----------------------------
# Dependency for FastAPI routes
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
