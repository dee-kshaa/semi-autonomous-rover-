from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, signals, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(signals.router)
api_router.include_router(analytics.router)
