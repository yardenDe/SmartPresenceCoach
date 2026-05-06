from models.session import Session as SessionModel

from core.exceptions import SessionNotFoundError, UnauthorizedError
from core.logger import get_logger
from db.buffer_manager import BufferManager
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository


class SessionService:
    def __init__(
        self,
        session_repository: SessionRepository,
        buffer_manager: BufferManager,
        snapshot_repository: SnapshotRepository,
    ):
        self.session_repository = session_repository
        self.buffer_manager = buffer_manager
        self.snapshot_repository = snapshot_repository
        self.logger = get_logger("app.sessions")

    def _get_session(self, user_id: int, session_id: int) -> SessionModel:
        session = self.session_repository.get_by_id(session_id)

        if not session:
            self.logger.warning("event=session.not_found session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        if session.user_id != user_id:
            self.logger.warning(
                "event=session.denied session_id=%s user_id=%s owner_id=%s",
                session_id,
                user_id,
                session.user_id,
            )
            raise UnauthorizedError()

        return session

    def create(self, user_id: int) -> int:
        session = self.session_repository.create_session(user_id=user_id)
        self.logger.info("event=session.create.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def start(self, user_id: int, session_id: int) -> int:
        self._get_session(user_id, session_id)
        session = self.session_repository.start_session(session_id=session_id)
        if not session:
            self.logger.warning("event=session.start.missing session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        self.logger.info("event=session.start.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def end(self, user_id: int, session_id: int) -> int:
        self._get_session(user_id, session_id)
        self._flush_pending_snapshots(session_id)
        session = self.session_repository.end_session(session_id=session_id)
        if not session:
            self.logger.warning("event=session.end.missing session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        self.logger.info("event=session.end.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def _flush_pending_snapshots(self, session_id: int) -> None:
        snapshots = self.buffer_manager.close_session(session_id)

        for snapshot in snapshots:
            self.snapshot_repository.create_snapshot(
                session_id=session_id,
                timestamp=snapshot.get("timestamp", 0.0),
                scores=snapshot,
            )

        if snapshots:
            self.logger.info(
                "event=session.buffer.flushed session_id=%s count=%s",
                session_id,
                len(snapshots),
            )
