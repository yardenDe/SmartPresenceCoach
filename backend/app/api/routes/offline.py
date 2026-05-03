from fastapi import APIRouter, Depends

from core.dependencies import get_offline_service
from core.logger import get_logger
from schemas.offline import OfflineVideoResponse
from services.offline_service import OfflineService


router = APIRouter(prefix="/offline", tags=["offline"])
logger = get_logger("app.routes.offline")


@router.post("/video", response_model=OfflineVideoResponse)
async def upload_and_analyze_video(
    offline_service: OfflineService = Depends(get_offline_service),
) -> OfflineVideoResponse:
    logger.info(
        "Received offline video upload for analysis",
    )
    result = await offline_service.process()

    return OfflineVideoResponse(
        result=result,
    )
