from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_id_by_username(self, user_name: str) -> int | None:
        query = select(User.id).where(User.username == user_name)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_password_by_id(self, user_id: int) -> str | None:
        query = select(User.hashed_password).where(User.id == user_id)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def create_user(self, user_name, hashed_password) -> int:
        user = User(username=user_name, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit() 
        return self.get_id_by_username(user_name)