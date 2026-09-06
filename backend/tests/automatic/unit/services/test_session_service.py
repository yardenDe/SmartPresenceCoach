from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def build_service(session):
    from services.session_service import SessionService

    session_repository = Mock()
    session_repository.get_by_id.return_value = session
    service = SessionService(
        session_repository=session_repository,
        session_buffer=Mock(),
        snapshot_repository=Mock(),
    )
    return service, session_repository


def test_require_owned_session_returns_the_users_session():
    session = SimpleNamespace(id=25, user_id=7)
    service, repository = build_service(session)

    result = service.require_owned_session(user_id=7, session_id=25)

    assert result is session
    repository.get_by_id.assert_called_once_with(25)


def test_require_owned_session_rejects_missing_session():
    from core.exceptions import SessionNotFoundError

    service, _ = build_service(None)

    with pytest.raises(SessionNotFoundError):
        service.require_owned_session(user_id=7, session_id=25)


def test_require_owned_session_rejects_another_users_session():
    from core.exceptions import UnauthorizedError

    service, _ = build_service(SimpleNamespace(id=25, user_id=8))

    with pytest.raises(UnauthorizedError):
        service.require_owned_session(user_id=7, session_id=25)


def test_add_analysis_buffers_and_persists_a_full_batch():
    from schemas.analysis import Analysis, VisualAnalysis
    from services.session_service import SessionService

    analysis = Analysis(
        visual=VisualAnalysis(overall=85.0, focus=80.0),
    )
    snapshots = [
        {"timestamp": 0.0, "analysis": analysis},
        {"timestamp": 3.0, "analysis": analysis},
    ]
    session_buffer = Mock()
    session_buffer.add.return_value = snapshots
    snapshot_repository = Mock()
    service = SessionService(
        session_repository=Mock(),
        session_buffer=session_buffer,
        snapshot_repository=snapshot_repository,
    )

    service.add_analysis(session_id=25, timestamp=3.0, analysis=analysis)

    session_buffer.add.assert_called_once_with(
        session_id=25,
        timestamp=3.0,
        analysis=analysis,
    )
    snapshot_repository.create_snapshots.assert_called_once_with(
        session_id=25,
        snapshots=snapshots,
    )


def test_flush_analysis_persists_pending_snapshots():
    from schemas.analysis import Analysis, VisualAnalysis
    from services.session_service import SessionService

    snapshots = [{
        "timestamp": 3.0,
        "analysis": Analysis(visual=VisualAnalysis(overall=85.0)),
    }]
    session_buffer = Mock()
    session_buffer.close_session.return_value = snapshots
    snapshot_repository = Mock()
    service = SessionService(
        session_repository=Mock(),
        session_buffer=session_buffer,
        snapshot_repository=snapshot_repository,
    )

    service.flush_analysis(session_id=25)

    session_buffer.close_session.assert_called_once_with(25)
    snapshot_repository.create_snapshots.assert_called_once_with(
        session_id=25,
        snapshots=snapshots,
    )
