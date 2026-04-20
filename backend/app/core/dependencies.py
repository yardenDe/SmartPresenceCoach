from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.excptions import InvalidCredentialsError
from core.security import TokenService
from db.db_manager import SessionLocal

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token_service = TokenService()
    payload = token_service.decode_token(credentials)
    user_id = payload.get("sub")

    if not user_id:
        raise InvalidCredentialsError()

    return int(user_id)


def get_session():
    pass