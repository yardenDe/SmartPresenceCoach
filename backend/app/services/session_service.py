from sqlalchemy.orm import Session

from core.excptions import SessionNotFoundError, UnauthorizedError
from repositories.session_repo import SessionRepo


class SessionService:
    def __init__(self, db: Session):
        self.session_repo = SessionRepo(db)

    def _get_session(self, user_id, session_id):
        session = self.session_repo.get_by_id(session_id)

        if not session:
            raise SessionNotFoundError()

        if session.user_id != user_id:
            raise UnauthorizedError()

        return session

    def create(self, user_id):
        session = self.session_repo.create_session(user_id=user_id)
        return session.id

    def start(self, user_id, session_id):
        self._get_session(user_id, session_id)
        session = self.session_repo.start_session(session_id=session_id)
        return session.id

    def end(self, user_id, session_id):
        self._get_session(user_id, session_id)
        session = self.session_repo.end_session(session_id=session_id)
        return session.id
