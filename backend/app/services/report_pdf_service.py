from reporting.pdf_renderer import ReportPdfRenderer
from services.report_service import ReportService


class ReportPdfService:
    def __init__(
        self,
        report_service: ReportService,
        pdf_renderer: ReportPdfRenderer,
    ):
        self.report_service = report_service
        self.pdf_renderer = pdf_renderer

    def build_full_report_pdf(self, user_id: int, session_id: int) -> bytes:
        report_data = self.report_service.get_full_report_data(user_id, session_id)
        return self.pdf_renderer.render(report_data)
