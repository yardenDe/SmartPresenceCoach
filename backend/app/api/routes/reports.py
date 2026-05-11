from fastapi import APIRouter, Depends

from core.dependencies import get_current_user_id, get_report_service
from schemas.report import ReportRespone
from services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{session_id}", response_model=ReportRespone)
def generate_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ReportRespone:
    return service.generate_report(session_id)

