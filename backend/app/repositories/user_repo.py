from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def create_user(self, username, password) -> User:
        user = User(username=username, password=password)
        self.db.add(user)
        self.db.commit() 
        self.db.refresh(user)
        return user
