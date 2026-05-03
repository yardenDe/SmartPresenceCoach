from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user_id
from core.logger import get_logger
from schemas.live import LiveRequest
from services.live_service import LiveService

router = APIRouter(prefix="/live", tags=["live"])
logger = get_logger("app.routes.live")


@router.post("/frame")
async def analyze_frame(
    request: LiveRequest = Depends(LiveRequest.as_form),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    logger.info(
        "Received live frame for session id=%s from user id=%s at timestamp=%s",
        request.session_id,
        user_id,
        request.timestamp,
    )

    live_service = LiveService(video=request.video)
    return live_service.process_frame(request.frame_data, request.session_id)
