from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from mediapipe.tasks.python.vision import RunningMode


class Settings(BaseSettings):
  
    DATABASE_URL: str

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 30
    

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"


    MEDIAPIPE_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent / "models" / "mediapipe")
    MEDIAPIPE_RUNNING_MODE: RunningMode = RunningMode.IMAGE
    FACE_LANDMARKER_MODEL: str = "face_landmarker.task"
    POSE_LANDMARKER_MODEL: str = "pose_landmarker.task"
    HAND_LANDMARKER_MODEL: str = "hand_landmarker.task"

    
    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
   

@lru_cache()
def get_settings():
    return Settings()
