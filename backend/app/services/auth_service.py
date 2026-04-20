from sqlalchemy.orm import Session
from core.excptions import (
    InvalidCredentialsError,
    InvalidUserNameError,
    UserNotFoundError,
)
from core.security import (
    TokenService,
    get_hashed_password,
    verify_password,
)
from repositories.user_repo import UserRepo

class AuthService:
    def __init__(self, db: Session):
        self.token_service = TokenService()
        self.user_repo = UserRepo(db)

    def register_user(self, username: str, password: str) -> tuple[int, str]:

        if self.user_repo.get_user_by_username(username):
            raise InvalidUserNameError()

        hashed_password = get_hashed_password(password)
        user = self.user_repo.create_user(username, hashed_password)
        
        return self.token_service.create_token(user.id)


    def login_user(self, username: str, password: str) -> tuple[int, str]:

        user = self.user_repo.get_user_by_username(username)
        if not user:
            raise UserNotFoundError()

        if not verify_password(password, user.password):
            raise InvalidCredentialsError()

        token = self.token_service.create_token(user.id)
        return user.id, token

    def me_user(self, token: str) -> int:

        payload = self.token_service.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidCredentialsError()
            
        return int(user_id)
