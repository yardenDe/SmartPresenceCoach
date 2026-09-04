from models.session import Session as SessionModel

from core.exceptions import SessionNotFoundError, UnauthorizedError
from core.logger import get_logger
from infrastructure.session_buffer import SessionBuffer
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.analysis import VisualAnalysis


class SessionService:
    def __init__(
        self,
        session_repository: SessionRepository,
        session_buffer: SessionBuffer,
        snapshot_repository: SnapshotRepository,
    ):
        self.session_repository = session_repository
        self.session_buffer = session_buffer
        self.snapshot_repository = snapshot_repository
        self.logger = get_logger("app.sessions")

    def require_owned_session(self, user_id: int, session_id: int) -> SessionModel:
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

    def create(self, user_id: int, mode: str | None = None) -> int:
        session = self.session_repository.create_session(user_id=user_id, mode=mode)
        self.logger.info("event=session.create.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def start(self, user_id: int, session_id: int) -> int:
        self.require_owned_session(user_id, session_id)
        session = self.session_repository.start_session(session_id=session_id)
        if not session:
            self.logger.warning("event=session.start.missing session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        self.logger.info("event=session.start.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def end(self, user_id: int, session_id: int) -> int:
        self.require_owned_session(user_id, session_id)
        self.flush_analysis(session_id)
        session = self.session_repository.end_session(session_id=session_id)
        if not session:
            self.logger.warning("event=session.end.missing session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        self.logger.info("event=session.end.done session_id=%s user_id=%s", session.id, user_id)
        return session.id

    def add_analysis(
        self,
        session_id: int,
        timestamp: float,
        analysis: VisualAnalysis,
    ) -> None:
        snapshots = self.session_buffer.add(
            session_id=session_id,
            snapshot={
                **analysis.model_dump(exclude_none=True),
                "timestamp": timestamp,
            },
        )

        if snapshots:
            self.snapshot_repository.create_snapshots(
                session_id=session_id,
                snapshots=snapshots,
            )

    def flush_analysis(self, session_id: int) -> None:
        snapshots = self.session_buffer.close_session(session_id)

        if snapshots:
            self.snapshot_repository.create_snapshots(
                session_id=session_id,
                snapshots=snapshots,
            )
            self.logger.info(
                "event=session.buffer.flushed session_id=%s count=%s",
                session_id,
                len(snapshots),
            )
