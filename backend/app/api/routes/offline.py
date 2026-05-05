from fastapi import APIRouter, Depends

from core.dependencies import get_offline_service
from schemas.offline import OfflineVideoResponse
from services.offline_service import OfflineService
from core.logger import get_logger

router = APIRouter(prefix="/offline", tags=["offline"])

logger = get_logger("app.services.offline")


@router.post("/video", response_model=OfflineVideoResponse)
async def upload_and_analyze_video(
    offline_service: OfflineService = Depends(get_offline_service),
) -> OfflineVideoResponse:

    logger.debug("event=offline.process.start")

    result = await offline_service.process()

    logger.info(
    "event=offline.process.result result=%s",
    result
)

    logger.debug("event=offline.process.done")

    return OfflineVideoResponse(result=result)