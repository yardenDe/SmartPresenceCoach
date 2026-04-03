from fastapi import APIRouter

from app.api.routes import auth, live, reports, sessions


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(live.router)
api_router.include_router(sessions.router)
api_router.include_router(reports.router)
