from fastapi import APIRouter
from backend.api import health, cache, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cache.router, prefix="/api", tags=["cache"])
api_router.include_router(ui.router, tags=["ui"])
