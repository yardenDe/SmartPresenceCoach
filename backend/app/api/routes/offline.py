from fastapi import APIRouter, Depends

from core.dependencies import get_offline_service
from schemas.offline import OfflineVideoResponse
from services.offline_service import OfflineService


router = APIRouter(prefix="/offline", tags=["offline"])


@router.post("/video", response_model=OfflineVideoResponse)
async def upload_and_analyze_video(
    offline_service: OfflineService = Depends(get_offline_service),
) -> OfflineVideoResponse:
    result = await offline_service.process()

    return OfflineVideoResponse(
        result=result,
    )
