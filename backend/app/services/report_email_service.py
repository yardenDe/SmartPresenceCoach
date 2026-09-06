from core.logger import get_logger
from infrastructure.email_engine import EmailEngine
from reporting.pdf_renderer import ReportPdfRenderer, report_pdf_filename
from reporting.templates import build_email_html
from schemas.report import ReportEmailResponse
from services.report_service import ReportService


class ReportEmailService:
    def __init__(
        self,
        report_service: ReportService,
        pdf_renderer: ReportPdfRenderer,
        email_engine: EmailEngine,
    ):
        self.report_service = report_service
        self.pdf_renderer = pdf_renderer
        self.email_engine = email_engine
        self.logger = get_logger("app.report_email")

    def send_full_report(
        self,
        user_id: int,
        session_id: int,
        to: str,
    ) -> ReportEmailResponse:
        report_data = self.report_service.get_full_report_data(user_id, session_id)
        html = build_email_html(report_data)
        pdf = self.pdf_renderer.render(report_data)
        self.email_engine.send(
            to=to,
            subject="Your Presence Report",
            body="Your full presence report is ready.",
            html=html,
            attachments=[
                (report_pdf_filename(session_id), pdf, "application/pdf"),
            ],
        )

        self.logger.info("event=report.email.sent session_id=%s", session_id)
        return ReportEmailResponse(status="sent")
