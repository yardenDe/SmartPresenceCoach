from fastapi import APIRouter, File, UploadFile

from core.logger import get_logger
from schemas.offline import OfflineVideoResponse
from services.offline_service import OfflineService


router = APIRouter(prefix="/offline", tags=["offline"])
logger = get_logger("app.routes.offline")


@router.post("/video", response_model=OfflineVideoResponse)
async def upload_and_analyze_video(
    video: UploadFile = File(...),
) -> OfflineVideoResponse:
    logger.info(
        "Received offline video upload for analysis",
    )

    offline_service = OfflineService(video=video)

    result = await offline_service.process()

    return OfflineVideoResponse(
        result=result,
    )
