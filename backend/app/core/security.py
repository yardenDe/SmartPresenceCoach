import jwt
from typing import Any
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer
import bcrypt

from core.exceptions import TokenExpiredError, InvalidTokenError
from core.config import get_settings
from core.logger import get_logger

settings = get_settings()
logger = get_logger("app/core/security")



class SecurityService:

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expire_minutes = settings.EXPIRE_MINUTES
        self.security = HTTPBearer()

    def create_token(self, user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(
        self, token: str
    ) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError
        except jwt.InvalidTokenError:
            raise InvalidTokenError

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

    @staticmethod
    def get_hashed_password(password: str) -> str:
        logger.info(f"Password type: {type(password)}")
        logger.info(f"Password length: {len(str(password))}")
        logger.info(f"Password full: {password}")

        bytes = password.encode("utf-8")
        return bcrypt.hashpw(bytes, bcrypt.gensalt()).decode("utf-8")
