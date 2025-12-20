# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # -----------------------------
    # Database Configuration
    # -----------------------------
    DATABASE_URL: str
    ASYNC_DATABASE_URL: Optional[str] = None
    TIMEZONE: str = "UTC"

    # -----------------------------
    # Application Settings
    # -----------------------------
    PROJECT_NAME: str = "Cinema Booking System"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["*"]

    # -----------------------------
    # Authentication / JWT
    # -----------------------------
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # -----------------------------
    # Email / NotificationContext
    # -----------------------------
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_PORT: int = 587

    # -----------------------------
    # Internal Event Bus
    # -----------------------------
    EVENT_BACKEND: str = "memory"
    CHANNEL_NAME: str = "domain_events"

    # -----------------------------
    # Payment Provider
    # -----------------------------
    PAYMENT_PROVIDER_API_KEY: str

    # -----------------------------
    # Default Admin
    # -----------------------------
    ADMIN_DEFAULT_EMAIL: str
    ADMIN_DEFAULT_PASSWORD: str

    # -----------------------------
    # Policies
    # -----------------------------
    RESERVATION_TIMEOUT_MINUTES: int = 15
    PAYMENT_TIMEOUT_MINUTES: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

