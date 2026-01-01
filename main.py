from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware

from app.contexts.auth.router import router as auth_router
from app.contexts.user.router import router as user_router
from app.contexts.movie.router import router as movie_router
from app.contexts.screen.router import router as screen_router
from app.contexts.showtime.router import router as showtime_router
from app.contexts.seat_availability.router import router as seat_availability_router
from app.contexts.reservation.router import router as reservation_router
from app.contexts.order.router import router as order_router
from app.contexts.pricing.router import router as pricing_router
from app.contexts.payment.router import router as payment_router
from app.contexts.refund.router import router as refund_router
from app.contexts.admin.router import router as admin_router

# Only import handlers that actually register events
from app.contexts.auth import handlers as auth_handlers
from app.contexts.user import handlers as user_handlers
from app.contexts.showtime import handlers as showtime_handlers
from app.contexts.seat_availability import handlers as seat_availability_handlers
from app.contexts.reservation import handlers as reservation_handlers
from app.contexts.order import handlers as order_handlers
from app.contexts.pricing import handlers as pricing_handlers
from app.contexts.payment import handlers as payment_handlers
from app.contexts.refund import handlers as refund_handlers
from app.contexts.notification import handlers as notification_handlers
from app.contexts.audit import handlers as audit_handlers

# Set up logging FIRST (before creating app)
setup_logging(log_level='DEBUG')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="DDD-based cinema booking system with event-driven architecture",
    version="1.0.0"
)

# Add middleware (ORDER MATTERS - RequestLogging should be first)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(screen_router)
app.include_router(showtime_router)
app.include_router(seat_availability_router)
app.include_router(reservation_router)
app.include_router(order_router)
app.include_router(pricing_router)
app.include_router(payment_router)
app.include_router(refund_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """Log all registered routes on startup"""
    logger.info("🎬 Cinema Booking System starting up...")
    logger.info("Registered routes:")
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ','.join(route.methods) if route.methods else 'UNKNOWN'
            logger.info(f"  {methods:10} {route.path}")
    
    logger.info("All event handlers registered")
    logger.info("System ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("Cinema Booking System shutting down...")


@app.get("/")
def root():
    """Root endpoint - health check"""
    logger.debug("Root endpoint hit")
    return {
        "status": "Cinema API running!",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "timestamp": "2024-12-27T12:00:00Z"
    }