from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.dependencies import get_current_user_id, get_live_service
from services.live_service import LiveService
from schemas.live import LiveResponse

router = APIRouter(prefix="/live", tags=["live"])


@router.post("/frame", response_model=LiveResponse)
async def analyze_frame(
    video: UploadFile = File(...),
    session_id: int = Form(...),
    user_id: int = Depends(get_current_user_id),
    live_service: LiveService = Depends(get_live_service)
) -> Any:
    result = await live_service.process(
        video=video,
        session_id=session_id,
    )

    return result
