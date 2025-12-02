# app/core/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Dict, Any


class AppError(Exception):
    """Base application-level error."""
    status_code = 500

    def __init__(self, message: str = "An application error occurred", context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}


# -----------------------------
# Common application errors
# -----------------------------
class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ValidationError(AppError):
    status_code = 400


# -----------------------------
# Domain-driven errors
# -----------------------------
class DomainError(AppError):
    status_code = 400


class InvariantViolation(DomainError):
    status_code = 422


class PermissionDenied(AppError):
    status_code = 403


async def handle_app_error(request: Request, exc: AppError):
    """Unified handler for all AppError subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "context": exc.context,
            }
        },
    )


def register_error_handlers(app):
    """Registers global FastAPI error mappings."""
    app.add_exception_handler(AppError, handle_app_error)
