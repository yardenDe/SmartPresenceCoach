from sqlalchemy.orm import Session

from app.core.execptions import (
    InvalidCredentialsError,
    InvalidUserNameError,
    UserNotFoundError,
    ValidationError,
)
from app.core.security import (
    TokenProvider,
    get_password_hash,
    verify_password,
)
from app.repositories.user import UserRepo


class Auth_Service:
    def __init__(self, db: Session):
        self.token_provider = TokenProvider()
        self.user_repo = UserRepo(db)

    def register_user(self, user_name: str, password: str) -> tuple[int, str]:
        user_id = self.user_repo.get_id_by_username(user_name)
        if user_id is not None:
            raise InvalidUserNameError()

        hashed_password = get_password_hash(password)
        user_id = self.user_repo.create_user(user_name, hashed_password)
        token = self.token_provider.generate_token(user_id)
        return user_id, token

    def login_user(self, user_name: str, password: str) -> tuple[int, str]:
        user_id = self.user_repo.get_id_by_username(user_name)
        if user_id is None:
            raise UserNotFoundError()

        hashed_password = self.user_repo.get_password_by_id(user_id)
        if not verify_password(password, hashed_password):
            raise InvalidCredentialsError()

        token = self.token_provider.generate_token(user_id)
        return user_id, token

    def me_user(self, user_name: str) -> int:
        pass

    def refresh_token(self, user_id: int) -> str:
        pass