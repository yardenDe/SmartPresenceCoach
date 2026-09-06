from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def build_report_service(report):
    from services.report_service import ReportService

    session_service = Mock()
    report_repository = Mock()
    report_repository.get_by_session.return_value = report
    service = ReportService(
        session_service=session_service,
        snapshot_repository=Mock(),
        report_repository=report_repository,
    )
    return service, session_service, report_repository


def test_get_full_report_data_validates_owner_and_returns_saved_data():
    report_data = {"session_id": 25, "summary": "Ready"}
    service, session_service, repository = build_report_service(
        SimpleNamespace(report_data=report_data)
    )

    result = service.get_full_report_data(user_id=7, session_id=25)

    assert result is report_data
    session_service.require_owned_session.assert_called_once_with(7, 25)
    repository.get_by_session.assert_called_once_with(25)


def test_get_full_report_data_rejects_missing_report():
    from core.exceptions import ReportNotFoundError

    service, _, _ = build_report_service(None)

    with pytest.raises(ReportNotFoundError):
        service.get_full_report_data(user_id=7, session_id=25)


def test_report_pdf_service_uses_report_service_as_data_source():
    from services.report_pdf_service import ReportPdfService

    report_data = {"session_id": 25}
    report_service = Mock()
    report_service.get_full_report_data.return_value = report_data
    pdf_renderer = Mock()
    pdf_renderer.render.return_value = b"pdf"
    service = ReportPdfService(
        report_service=report_service,
        pdf_renderer=pdf_renderer,
    )

    result = service.build_full_report_pdf(user_id=7, session_id=25)

    assert result == b"pdf"
    report_service.get_full_report_data.assert_called_once_with(7, 25)
    pdf_renderer.render.assert_called_once_with(report_data)


def test_report_email_service_builds_and_sends_the_saved_report(monkeypatch):
    import services.report_email_service as report_email_service_module

    report_data = {"session_id": 25}
    report_service = Mock()
    report_service.get_full_report_data.return_value = report_data
    pdf_renderer = Mock()
    pdf_renderer.render.return_value = b"pdf"
    email_engine = Mock()
    monkeypatch.setattr(
        report_email_service_module,
        "build_email_html",
        Mock(return_value="<html />"),
    )
    service = report_email_service_module.ReportEmailService(
        report_service=report_service,
        pdf_renderer=pdf_renderer,
        email_engine=email_engine,
    )

    response = service.send_full_report(
        user_id=7,
        session_id=25,
        to="user@example.com",
    )

    assert response.status == "sent"
    report_service.get_full_report_data.assert_called_once_with(7, 25)
    pdf_renderer.render.assert_called_once_with(report_data)
    email_engine.send.assert_called_once_with(
        to="user@example.com",
        subject="Your Presence Report",
        body="Your full presence report is ready.",
        html="<html />",
        attachments=[("presence-report-25.pdf", b"pdf", "application/pdf")],
    )
