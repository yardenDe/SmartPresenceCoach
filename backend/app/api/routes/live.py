from typing import Any

from fastapi import APIRouter, Depends

from core.dependencies import get_current_user_id, get_live_service
from core.logger import get_logger
from schemas.live import LiveRequest
from services.live_service import LiveService

router = APIRouter(prefix="/live", tags=["live"])
logger = get_logger("app.routes.live")


@router.post("/frame")
async def analyze_frame(
    request: LiveRequest = Depends(LiveRequest),
    user_id: int = Depends(get_current_user_id),
    live_service: LiveService = Depends(get_live_service)
) -> Any:
    logger.info(
        "Received live frame for session id=%s from user id=%s at timestamp=%s",
        request.session_id,
        user_id,
        request.timestamp,
    )

    return live_service.process_frame(request.frame_data, request.session_id)
