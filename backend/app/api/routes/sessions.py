from fastapi import APIRouter, Depends

from core.dependencies import get_current_user_id, get_session_service
from schemas.session import CreateSessionRequest
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create")
def create_session(
    request: CreateSessionRequest | None = None,
    user_id: int = Depends(get_current_user_id),
    service: SessionService = Depends(get_session_service),
) -> int:
    return service.create(user_id, request.mode if request else None)


@router.post("/start/{session_id}")
def start_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: SessionService = Depends(get_session_service),
) -> int:
    return service.start(user_id, session_id)


@router.post("/end/{session_id}")
def end_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: SessionService = Depends(get_session_service),
) -> int:
    return service.end(user_id, session_id)
