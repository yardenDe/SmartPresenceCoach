from fastapi import APIRouter, Depends

from core.dependencies import (
    get_current_user_id,
    get_report_service,
    get_llm_service,
)
from schemas.report import (
    FullReportResponse,
    RecentReportResponse,
    ShortReportResponse,
)
from services.report_service import ReportService
from services.llm_service import LLMService

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/recent", response_model=list[RecentReportResponse])
def recent_reports(
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> list[RecentReportResponse]:
    return service.list_recent_reports(user_id=user_id)


@router.post("/{session_id}/short", response_model=ShortReportResponse)
def generate_short_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ShortReportResponse:
    return service.generate_report(
        user_id=user_id,
        session_id=session_id,
        full=False,
    )


@router.post("/{session_id}/full", response_model=FullReportResponse)
def generate_full_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
    llm_service: LLMService | None = Depends(get_llm_service),
) -> FullReportResponse:
    return service.generate_report(
        user_id=user_id,
        session_id=session_id,
        full=True,
        llm_service=llm_service,
    )
