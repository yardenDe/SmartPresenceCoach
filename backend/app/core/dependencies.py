from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.exceptions import InvalidCredentialsError
from core.security import TokenService
from db.db_manager import SessionLocal

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        
        db.close()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token_service = TokenService()
    token = credentials.credentials

    payload = token_service.decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise InvalidCredentialsError()

    return int(user_id)


def get_session() -> None:
    pass
