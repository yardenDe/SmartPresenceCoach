from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from mediapipe.tasks.python.vision import RunningMode


class Settings(BaseSettings):
  
    DATABASE_URL: str = "sqlite:///./data/sql_app.db"

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 30
    
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    RELOAD: bool = False

    FRONTEND_ORIGIN: str = "http://localhost:5173"
    LOG_LEVEL: str = "DEBUG"

    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    LLM_TEMPERATURE: float = 1.0
    LLM_MAX_OUTPUT_TOKENS: int = 4096

    TRANSCRIBER_MODEL: str = "base"

    MEDIAPIPE_MODEL_PATH: str = str(Path(__file__).resolve().parents[2] / "assets" / "mediapipe")
    MEDIAPIPE_RUNNING_MODE: RunningMode = RunningMode.IMAGE
    FACE_LANDMARKER_MODEL: str = "face_landmarker.task"
    POSE_LANDMARKER_MODEL: str = "pose_landmarker.task"
    HAND_LANDMARKER_MODEL: str = "hand_landmarker.task"

    MAIL_HOST: str | None = None
    MAIL_PORT: int = 587
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    MAIL_TIMEOUT: float = 10.0
    

    
    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
   

@lru_cache()
def get_settings() -> Settings:
    return Settings()
