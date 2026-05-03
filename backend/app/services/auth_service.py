from core.exceptions import (
    InvalidCredentialsError,
    InvalidUserNameError,
    UserNotFoundError,
)
from core.security import SecurityService
from core.logger import get_logger
from repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository, security_service: SecurityService):
        self.security_service = security_service
        self.user_repository = user_repository
        self.logger = get_logger("app.auth")

    def register_user(self, username: str, password: str) -> str:
        self.logger.info("Trying to register user '%s'", username)

        if self.user_repository.get_user_by_username(username):
            self.logger.warning("Register failed because username '%s' already exists", username)
            raise InvalidUserNameError()

        hashed_password = self.security_service.get_hashed_password(password)
        user = self.user_repository.create_user(username, hashed_password)
        self.logger.info("User '%s' registered successfully with id=%s", username, user.id)
        
        return self.security_service.create_token(user.id)


    def login_user(self, username: str, password: str) -> str:
        self.logger.info("Login attempt for user '%s'", username)

        user = self.user_repository.get_user_by_username(username)
        if not user:
            self.logger.warning("Login failed because user '%s' was not found", username)
            raise UserNotFoundError()

        if not self.security_service.verify_password(password, user.password):
            self.logger.warning("Login failed because password did not match for user '%s'", username)
            raise InvalidCredentialsError()

        token = self.security_service.create_token(user.id)
        self.logger.info("User '%s' logged in successfully", username)
        return token

    def me_user(self, token: str) -> int:
        self.logger.info("Resolving current user from token")
        payload = self.security_service.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            self.logger.warning("Token payload does not include user id")
            raise InvalidCredentialsError()
            
        self.logger.info("Resolved current user id=%s from token", user_id)
        return int(user_id)
