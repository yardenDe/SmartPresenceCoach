from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register():
    return {"message": "Register endpoint"}

@router.post("/login")
async def login():
    return {"message": "Login endpoint"}

@router.get("/me")
async def get_current_user():
    return {"message": "Current user endpoint"}

@router.post("/refresh-token")
async def refresh_token():
    return {"message": "Refresh token endpoint"}
