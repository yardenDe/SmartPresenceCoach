import jwt
from typing import Any
from datetime import datetime, timedelta, timezone
import bcrypt

from core.exceptions import TokenExpiredError, InvalidTokenError
from core.config import get_settings

settings = get_settings()



class SecurityService:

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expire_minutes = settings.EXPIRE_MINUTES

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
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False

    @staticmethod
    def get_hashed_password(password: str) -> str:
        bytes = password.encode("utf-8")
        return bcrypt.hashpw(bytes, bcrypt.gensalt()).decode("utf-8")
