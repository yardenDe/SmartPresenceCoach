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


def test_add_snapshot_preserves_objects_through_buffer_and_repository():
    from infrastructure.session_buffer import SessionBuffer
    from models.snapshot import Snapshot
    from services.session_service import SessionService

    repository = Mock()
    buffer = SessionBuffer(flush_size=2)
    service = SessionService(Mock(), buffer, repository)
    first = Snapshot(session_id=25, timestamp=0.0, gaze_direction=0.0)
    second = Snapshot(session_id=25, timestamp=3.0, average_volume=-19.0)

    service.add_snapshot(first)
    repository.create_snapshots.assert_not_called()
    service.add_snapshot(second)
    repository.create_snapshots.assert_called_once_with(snapshots=[first, second])


def test_flush_snapshots_persists_pending_snapshot():
    from infrastructure.session_buffer import SessionBuffer
    from models.snapshot import Snapshot
    from services.session_service import SessionService

    buffer = SessionBuffer(flush_size=2)
    repository = Mock()
    service = SessionService(Mock(), buffer, repository)
    snapshot = Snapshot(session_id=25, timestamp=3.0, gaze_direction=4.0)
    service.add_snapshot(snapshot)
    service.flush_snapshots(25)
    repository.create_snapshots.assert_called_once_with(snapshots=[snapshot])
    assert 25 not in buffer.buffers
