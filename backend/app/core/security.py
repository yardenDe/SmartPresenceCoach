import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt

from core.exceptions import TokenExpiredError, InvalidTokenError
from core.config import get_settings
from core.logger import get_logger

settings = get_settings()
logger = get_logger("app/core/security")

def verify_password(password: str, hashed_password: str) -> bool:
    bytes = password.encode("utf-8")
    return bcrypt.checkpw(bytes, hashed_password)

def get_hashed_password(password: str) -> str:
    logger.info(f"Password type: {type(password)}")
    logger.info(f"Password length: {len(str(password))}")
    logger.info(f"Password full: {password}")

    bytes = password.encode("utf-8")
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class TokenService:

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expire_minutes = settings.EXPIRE_MINUTES
        self.security = HTTPBearer()

    def create_token(self, username: int) -> str:
        payload = {
            "sub": username,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(
        self, credentials: HTTPAuthorizationCredentials
    ) -> dict:
        token = credentials.credentials
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
        
   
    
