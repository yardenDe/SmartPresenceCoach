from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.dependencies import get_current_user_id, get_live_service
from services.live_service import LiveService
from schemas.live import LiveResponse

router = APIRouter(prefix="/live", tags=["live"])


@router.post("/chunk", response_model=LiveResponse)
async def analyze_chunk(
    video: UploadFile = File(...),
    session_id: int = Form(...),
    timestamp: float = Form(0.0),
    user_id: int = Depends(get_current_user_id),
    live_service: LiveService = Depends(get_live_service)
) -> LiveResponse:
    result = await live_service.process(
        video=video,
        user_id=user_id,
        session_id=session_id,
        timestamp=timestamp,
    )

    return result
