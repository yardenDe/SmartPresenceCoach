from fastapi import APIRouter, Depends, Form

from core.dependencies import get_current_user_id, get_offline_service
from schemas.offline import OfflineResponse
from services.offline_service import OfflineService
from core.logger import get_logger

router = APIRouter(prefix="/offline", tags=["offline"])

logger = get_logger("app.services.offline")


@router.post("/video", response_model=OfflineResponse)
async def upload_and_analyze_video(
    session_id: int = Form(...),
    user_id: int = Depends(get_current_user_id),
    offline_service: OfflineService = Depends(get_offline_service),
) -> OfflineResponse:
    _ = user_id

    logger.debug("event=offline.process.start")

    result = await offline_service.process(session_id=session_id)

    logger.info(
        "event=offline.process.result result=%s",
        result,
    )

    logger.debug("event=offline.process.done")

    return result
