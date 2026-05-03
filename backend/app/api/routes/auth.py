from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from core.logger import get_logger
from services.auth_service import AuthService
from schemas.auth import ( 
    UserCreate,
    UserLogin,
    Token
)

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("app.routes.auth")

@router.post("/register", response_model=Token)
async def register(request: UserCreate, db: Session = Depends(get_db)) -> Token:
    logger.info("Received register request for username '%s'", request.username)
    auth_service = AuthService(db)
    token = auth_service.register_user(request.username, request.password)
    
    return Token(access_token=token)

@router.post("/login", response_model=Token)
async def login(request: UserLogin, db: Session = Depends(get_db)) -> Token:
    logger.info("Received login request for username '%s'", request.username)
    auth_service = AuthService(db)
    token = auth_service.login_user(request.username, request.password)
    
    return Token(access_token=token)


@router.get("/me")
async def get_me() -> None:
    pass
