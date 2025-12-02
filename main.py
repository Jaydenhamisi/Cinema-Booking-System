from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.contexts.screen.router import router as screen_router
from app.contexts.showtime.router import router as showtime_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screen_router)
app.include_router(showtime_router)

@app.get("/")
def root():
    return {"status": "Cinema API running!"}
