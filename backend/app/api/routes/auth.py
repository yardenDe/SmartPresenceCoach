from fastapi import APIRouter, Depends

from core.dependencies import get_auth_service
from services.auth_service import AuthService
from schemas.auth import ( 
    UserCreate,
    UserLogin,
    Token
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(request: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> Token:
    token = auth_service.register_user(request.username, request.password)
    
    return Token(access_token=token)

@router.post("/login", response_model=Token)
async def login(request: UserLogin, auth_service: AuthService = Depends(get_auth_service)) -> Token:
    token = auth_service.login_user(request.username, request.password)
    
    return Token(access_token=token)


@router.get("/me")
async def get_me() -> None:
    pass
