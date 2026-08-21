from fastapi import APIRouter

from api.routes import auth, live, offline, reports, sessions, health


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(live.router)
api_router.include_router(offline.router)
api_router.include_router(sessions.router)
api_router.include_router(reports.router)
api_router.include_router(health.router)


