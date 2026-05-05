from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User
from core.exceptions import DatabaseError
from core.logger import get_logger

logger = get_logger("app.repositories.user")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        try:
            query = select(User).where(User.username == username)
            result = self.db.execute(query)
            user = result.scalar_one_or_none()
        except Exception:
            logger.exception("event=user.lookup.failed")
            raise DatabaseError()

        logger.debug("event=user.lookup.done found=%s", user is not None)
        return user

    def create_user(self, username: str, password: str) -> User:
        user = User(username=username, password=password)
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except Exception:
            self.db.rollback()
            logger.exception("event=user.create.failed")
            raise DatabaseError()

        logger.info("event=user.create.done user_id=%s", user.id)
        return user
