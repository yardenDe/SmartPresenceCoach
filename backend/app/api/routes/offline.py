from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.dependencies import get_current_user_id, get_offline_service
from schemas.offline import OfflineResponse
from services.offline_service import OfflineService

router = APIRouter(prefix="/offline", tags=["offline"])


@router.post("/video", response_model=OfflineResponse)
async def upload_and_analyze_video(
    video: UploadFile = File(...),
    session_id: int = Form(...),
    user_id: int = Depends(get_current_user_id),
    offline_service: OfflineService = Depends(get_offline_service),
) -> OfflineResponse:
    return await offline_service.process(
        video=video,
        user_id=user_id,
        session_id=session_id,
    )
