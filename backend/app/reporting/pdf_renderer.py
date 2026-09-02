from core.exceptions import PdfUnavailableError
from reporting.templates import build_pdf_html


class ReportPdfRenderer:
    def render(self, report_data: dict) -> bytes:
        try:
            from weasyprint import HTML

            html = build_pdf_html(report_data)
            return HTML(string=html).write_pdf()
        except Exception as error:
            raise PdfUnavailableError() from error


def report_pdf_filename(session_id: int) -> str:
    return f"presence-report-{session_id}.pdf"
