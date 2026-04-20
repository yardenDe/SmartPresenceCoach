from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user_id
from services.session_service import SessionService


from schemas.live import FrameRequest
router = APIRouter(prefix="/live", tags=["live"])


@router.post("/frame")
async def analyze_frame(
    request: FrameRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    session_service = SessionService(db)

    return {"message": "frame endpoint"}
