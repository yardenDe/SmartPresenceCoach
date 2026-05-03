from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user_id
from core.logger import get_logger
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = get_logger("app.routes.sessions")


@router.post("/create")
def create_session(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> int:
    logger.info("Received create session request for user id=%s", user_id)
    service = SessionService(db)
    return service.create(user_id)


@router.post("/start/{session_id}")
def start_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> int:
    logger.info("Received start session request for session id=%s, user id=%s", session_id, user_id)
    service = SessionService(db)
    return service.start(user_id, session_id)


@router.post("/end/{session_id}")
def end_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> int:
    logger.info("Received end session request for session id=%s, user id=%s", session_id, user_id)
    service = SessionService(db)
    return service.end(user_id, session_id)
