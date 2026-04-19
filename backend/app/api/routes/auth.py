from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from services.auth_service import AuthService
from schemas.user import ( 
    UserCreate,
    UserLogin,
    Token
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(request: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    token = auth_service.register_user(request.username, request.password)
    
    return Token(access_token=token)

@router.post("/login", response_model=Token)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    token = auth_service.login_user(request.username, request.password)
    
    return Token(access_token=token)


@router.get("/me")
async def get_me():
    pass