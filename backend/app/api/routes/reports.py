from fastapi import APIRouter, Depends, Response

from core.dependencies import (
    get_current_user_id,
    get_email_service,
    get_report_pdf_service,
    get_report_service,
    get_llm_service,
)
from schemas.report import (
    FullReportResponse,
    RecentReportResponse,
    ReportEmailRequest,
    ReportEmailResponse,
    ShortReportResponse,
)
from services.email_service import EmailService
from services.report_pdf_service import ReportPdfService
from services.report_service import ReportService
from services.llm_service import LLMService

router = APIRouter(prefix="/reports", tags=["reports"])

SHORT_REPORT_FIELDS = {"overall_score", "overall_state", "timeline", "metrics"}
FULL_REPORT_FIELDS = {*SHORT_REPORT_FIELDS, "summary", "recommendations"}


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
    return ShortReportResponse.model_validate(
        service.generate_report(
            user_id=user_id,
            session_id=session_id,
            fields=SHORT_REPORT_FIELDS,
        )
    )


@router.post("/{session_id}/full", response_model=FullReportResponse)
def generate_full_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
    llm_service: LLMService | None = Depends(get_llm_service),
) -> FullReportResponse:
<<<<<<< Updated upstream
    return service.generate_full_report(user_id=user_id, session_id=session_id, llm_service=llm_service)
=======
    return FullReportResponse.model_validate(
        service.generate_report(
            user_id=user_id,
            session_id=session_id,
            fields=FULL_REPORT_FIELDS,
            llm_service=llm_service,
        )
    )
>>>>>>> Stashed changes


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


@router.get("/{session_id}/pdf")
def download_full_report_pdf(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportPdfService = Depends(get_report_pdf_service),
) -> Response:
    pdf = service.build_full_report_pdf(user_id=user_id, session_id=session_id)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="presence-analysis-{session_id}.pdf"',
        },
    )
