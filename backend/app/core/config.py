from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
  
    DATABASE_URL: str

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 30
    

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    
    class Config:
        env_file = ".env"
   

@lru_cache()
def get_settings():
    return Settings()