import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

settings = get_settings()

class TokenProvider:

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expire_minutes = settings.EXPIRE_MINUTES
        self.security = HTTPBearer()

    def generate_token(self, user_id: int) -> str:
        payload = {
            "sub": user_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(
        self, credentials: HTTPAuthorizationCredentials
    ) -> dict:
        token = credentials.credentials
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
