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
        self.logger = get_logger("app.services.auth")

    def register_user(self, username: str, password: str) -> str:
        self.logger.info("event=auth.register.start username=%s", username)

        if self.user_repository.get_user_by_username(username):
            self.logger.warning("event=auth.register.exists username=%s", username)
            raise InvalidUserNameError()

        hashed_password = self.security_service.get_hashed_password(password)
        user = self.user_repository.create_user(username, hashed_password)
        self.logger.info("event=auth.register.done user_id=%s username=%s", user.id, username)
        
        return self.security_service.create_token(user.id)


    def login_user(self, username: str, password: str) -> str:
        self.logger.info("event=auth.login.start username=%s", username)

        user = self.user_repository.get_user_by_username(username)
        if not user:
            self.logger.warning("event=auth.login.not_found username=%s", username)
            raise UserNotFoundError()

        if not self.security_service.verify_password(password, user.password):
            self.logger.warning("event=auth.login.bad_password username=%s", username)
            raise InvalidCredentialsError()

        token = self.security_service.create_token(user.id)
        self.logger.info("event=auth.login.done user_id=%s username=%s", user.id, username)
        return token

    def me_user(self, token: str) -> int:
        payload = self.security_service.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            self.logger.warning("event=auth.token.missing_sub")
            raise InvalidCredentialsError()
            
        return int(user_id)
