from sqlalchemy.orm import Session
from core.exceptions import (
    InvalidCredentialsError,
    InvalidUserNameError,
    UserNotFoundError,
)
from core.security import (
    TokenService,
    get_hashed_password,
    verify_password,
)
from core.logger import get_logger
from repositories.UserRepository import UserRepo

class AuthService:
    def __init__(self, db: Session) -> None:
        self.token_service = TokenService()
        self.user_repo = UserRepo(db)
        self.logger = get_logger("app.auth")

    def register_user(self, username: str, password: str) -> str:
        self.logger.info("Trying to register user '%s'", username)

        if self.user_repo.get_user_by_username(username):
            self.logger.warning("Register failed because username '%s' already exists", username)
            raise InvalidUserNameError()

        hashed_password = get_hashed_password(password)
        user = self.user_repo.create_user(username, hashed_password)
        self.logger.info("User '%s' registered successfully with id=%s", username, user.id)
        
        return self.token_service.create_token(user.id)


    def login_user(self, username: str, password: str) -> str:
        self.logger.info("Login attempt for user '%s'", username)

        user = self.user_repo.get_user_by_username(username)
        if not user:
            self.logger.warning("Login failed because user '%s' was not found", username)
            raise UserNotFoundError()

        if not verify_password(password, user.password):
            self.logger.warning("Login failed because password did not match for user '%s'", username)
            raise InvalidCredentialsError()

        token = self.token_service.create_token(user.id)
        self.logger.info("User '%s' logged in successfully", username)
        return token

    def me_user(self, token: str) -> int:
        self.logger.info("Resolving current user from token")
        payload = self.token_service.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            self.logger.warning("Token payload does not include user id")
            raise InvalidCredentialsError()
            
        self.logger.info("Resolved current user id=%s from token", user_id)
        return int(user_id)
