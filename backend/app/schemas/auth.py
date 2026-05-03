from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(UserLogin):
    pass


class UserRead(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
