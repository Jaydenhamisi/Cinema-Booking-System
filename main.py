from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
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

from app.contexts.auth import handlers as auth_handlers
from app.contexts.user import handlers as user_handlers
from app.contexts.movie import handlers as movie_handlers
from app.contexts.screen import handlers as screen_handlers
from app.contexts.showtime import handlers as showtime_handlers
from app.contexts.seat_availability import handlers as seat_availability_handlers
from app.contexts.reservation import handlers as reservation_handlers
from app.contexts.order import handlers as order_handlers
from app.contexts.pricing import handlers as pricing_handlers
from app.contexts.payment import handlers as payment_handlers
from app.contexts.refund import handlers as refund_handlers
from app.contexts.notification import handlers as notification_handlers
from app.contexts.audit import handlers as audit_handlers

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def root():
    return {"status": "Cinema API running!"}
