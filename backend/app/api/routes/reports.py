from fastapi import APIRouter, Depends

from core.dependencies import get_current_user_id, get_email_service, get_report_service
from schemas.report import (
    FullReportResponse,
    ReportEmailRequest,
    ReportEmailResponse,
    ShortReportResponse,
)
from services.email_service import EmailService
from services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{session_id}/short", response_model=ShortReportResponse)
def generate_short_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ShortReportResponse:
    return service.generate_short_report(user_id=user_id, session_id=session_id)


@router.post("/{session_id}/full", response_model=FullReportResponse)
def generate_full_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> FullReportResponse:
    return service.generate_full_report(user_id=user_id, session_id=session_id)


@router.post("/{session_id}/email", response_model=ReportEmailResponse)
def send_full_report_email(
    session_id: int,
    request: ReportEmailRequest,
    user_id: int = Depends(get_current_user_id),
    service: EmailService = Depends(get_email_service),
) -> ReportEmailResponse:
    return service.send_full_report(
        user_id=user_id,
        session_id=session_id,
        to=request.to,
    )
