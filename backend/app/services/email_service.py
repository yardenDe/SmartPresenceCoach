from core.exceptions import ReportNotFoundError, SessionNotFoundError, UnauthorizedError
from core.logger import get_logger
from repositories.report_repository import ReportRepository
from repositories.session_repository import SessionRepository
from services.email_engine import EmailEngine
from services.report_pdf_service import build_pdf_bytes
from services.report_templates import build_email_html


class EmailService:
    def __init__(
        self,
        session_repository: SessionRepository,
        report_repository: ReportRepository,
        email_engine: EmailEngine,
    ):
        self.session_repository = session_repository
        self.report_repository = report_repository
        self.email_engine = email_engine
        self.logger = get_logger("app.email_service")

    def send_full_report(self, user_id: int, session_id: int, to: str) -> dict:
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError()

        if session.user_id != user_id:
            raise UnauthorizedError()

        report = self.report_repository.get_by_session(session_id)
        if not report or not report.report_data:
            raise ReportNotFoundError()

        html = build_email_html(report.report_data)
        pdf = build_pdf_bytes(report.report_data)
        self.email_engine.send_email(
            to=to,
            subject="Your Presence Report",
            body="Your full presence report is ready.",
            html=html,
            attachments=[
                (f"presence-report-{session_id}.pdf", pdf, "application/pdf"),
            ],
        )

        self.logger.info(
            "event=report.email.sent session_id=%s report_id=%s to=%s",
            session_id,
            report.id,
            to,
        )
        return {"status": "sent"}
