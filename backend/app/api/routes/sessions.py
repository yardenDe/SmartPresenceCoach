from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user_id
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create")
def create_session(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return service.create(user_id)


@router.post("/start/{session_id}")
def start_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return service.start(session_id, user_id)


@router.post("/end/{session_id}")
def end_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    service = SessionService(db)
    return service.end(session_id, user_id)
