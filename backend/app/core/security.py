import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from core.excptions import TokenExpiredError, InvalidTokenError
from core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


class TokenService:

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expire_minutes = settings.EXPIRE_MINUTES
        self.security = HTTPBearer()

    def     create_token(self, username: int) -> str:
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
        
   
    
