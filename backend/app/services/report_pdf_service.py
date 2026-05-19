from core.exceptions import PdfUnavailableError, ReportNotFoundError, SessionNotFoundError, UnauthorizedError
from repositories.report_repository import ReportRepository
from repositories.session_repository import SessionRepository
from services.report_templates import build_pdf_html


class ReportPdfService:
    def __init__(
        self,
        session_repository: SessionRepository,
        report_repository: ReportRepository,
    ):
        self.session_repository = session_repository
        self.report_repository = report_repository

    def build_full_report_pdf(self, user_id: int, session_id: int) -> bytes:
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError()

        if session.user_id != user_id:
            raise UnauthorizedError()

        report = self.report_repository.get_by_session(session_id)
        if not report or not report.report_data:
            raise ReportNotFoundError()

        return build_pdf_bytes(report.report_data)


def build_pdf_bytes(report_data: dict) -> bytes:
    try:
        from weasyprint import HTML
    except Exception as error:
        raise PdfUnavailableError() from error

    html = build_pdf_html(report_data)
    return HTML(string=html).write_pdf()
