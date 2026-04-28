from sqlalchemy.orm import Session

from core.exceptions import SessionNotFoundError, UnauthorizedError
from core.logger import get_logger
from repositories.session_repo import SessionRepo


class SessionService:
    def __init__(self, db: Session):
        self.session_repo = SessionRepo(db)
        self.logger = get_logger("app.sessions")

    def _get_session(self, user_id, session_id):
        self.logger.info("Loading session id=%s for user id=%s", session_id, user_id)
        session = self.session_repo.get_by_id(session_id)

        if not session:
            self.logger.warning("Session id=%s was not found", session_id)
            raise SessionNotFoundError()

        if session.user_id != user_id:
            self.logger.warning(
                "User id=%s tried to access session id=%s owned by user id=%s",
                user_id,
                session_id,
                session.user_id,
            )
            raise UnauthorizedError()

        return session

    def create(self, user_id):
        session = self.session_repo.create_session(user_id=user_id)
        self.logger.info("Created session id=%s for user id=%s", session.id, user_id)
        return session.id

    def start(self, user_id, session_id):
        self._get_session(user_id, session_id)
        session = self.session_repo.start_session(session_id=session_id)
        self.logger.info("Started session id=%s for user id=%s", session.id, user_id)
        return session.id

    def end(self, user_id, session_id):
        self._get_session(user_id, session_id)
        session = self.session_repo.end_session(session_id=session_id)
        self.logger.info("Ended session id=%s for user id=%s", session.id, user_id)
        return session.id
