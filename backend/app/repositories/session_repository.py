from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from core.exceptions import DatabaseError
from core.logger import get_logger
from models.session import Session

logger = get_logger("app.repositories.session")


class SessionRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_session(self, user_id: int) -> Session:
        session = Session(user_id=user_id)

        try:
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        except Exception:
            self.db.rollback()
            logger.exception("event=session.create.failed")
            raise DatabaseError()

        logger.info("event=session.create.saved session_id=%s user_id=%s", session.id, user_id)
        return session

    def start_session(self, session_id: int) -> Session | None:
        session = self.db.get(Session, session_id)
        if not session:
            return None

        try:
            session.start_time = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(session)
        except Exception:
            self.db.rollback()
            logger.exception("event=session.start.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.info("event=session.start.saved session_id=%s", session_id)
        return session

    def end_session(self, session_id: int) -> Session | None:
        session = self.db.get(Session, session_id)
        if not session:
            return None

        try:
            session.end_time = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(session)
        except Exception:
            self.db.rollback()
            logger.exception("event=session.end.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.info("event=session.end.saved session_id=%s", session_id)
        return session


    def get_by_id(self, session_id: int) -> Session | None:
        try:
            query = select(Session).where(Session.id == session_id)
            session = self.db.execute(query).scalar_one_or_none()
        except Exception:
            logger.exception("event=session.lookup.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.debug(
            "event=session.lookup.done session_id=%s found=%s",
            session_id,
            session is not None,
        )
        return session

