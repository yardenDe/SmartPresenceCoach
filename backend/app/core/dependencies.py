from typing import Generator

from fastapi import Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.logger import get_logger
from core.exceptions import InvalidCredentialsError
from core.security import SecurityService
from db.db_manager import SessionLocal
from db.buffer_manager import BufferManager
from analytics.manager import AnalyticsManager
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.live_service import LiveService
from services.offline_service import OfflineService
from services.session_service import SessionService
from vision.mediapipe_detector import MediaPipeDetector
from vision.video_storage import VideoStorage

security = HTTPBearer()

logger = get_logger("app.core.dependencies")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        
        db.close()


def get_security_service() -> SecurityService:
    return SecurityService()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_session_repository(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


def get_snapshot_repository(db: Session = Depends(get_db)) -> SnapshotRepository:
    return SnapshotRepository(db)


def get_analytics_manager() -> AnalyticsManager:
    return AnalyticsManager()


def get_video_storage() -> VideoStorage:
    return VideoStorage()


_detector_instance = None
_buffer_manager = BufferManager()

def get_mp_detector() -> MediaPipeDetector:
  
    global _detector_instance
    if _detector_instance is None:
        logger.info("event=mediapipe.load.start")
        _detector_instance = MediaPipeDetector()
        logger.info("event=mediapipe.load.done")
    return _detector_instance


def close_mp_detector() -> None:
    global _detector_instance

    if _detector_instance is None:
        return

    logger.info("event=mediapipe.close.start")
    try:
        _detector_instance.close()
    except Exception:
        logger.exception("event=mediapipe.close.failed")
    finally:
        _detector_instance = None
        logger.info("event=mediapipe.close.done")


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    security_service: SecurityService = Depends(get_security_service),
) -> int:
    token = credentials.credentials

    payload = security_service.decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise InvalidCredentialsError()

    return int(user_id)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    security_service: SecurityService = Depends(get_security_service),
) -> AuthService:
    return AuthService(user_repository=user_repository, security_service=security_service)


def get_buffer_manager() -> BufferManager:
    return _buffer_manager


def get_session_service(
    session_repository: SessionRepository = Depends(get_session_repository),
    buffer_manager: BufferManager = Depends(get_buffer_manager),
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository),
) -> SessionService:
    return SessionService(
        session_repository=session_repository,
        buffer_manager=buffer_manager,
        snapshot_repository=snapshot_repository,
    )


def get_live_service(
    analytics: AnalyticsManager = Depends(get_analytics_manager),
    video_storage: VideoStorage = Depends(get_video_storage),
    detector: MediaPipeDetector = Depends(get_mp_detector),
    buffer_manager: BufferManager = Depends(get_buffer_manager),
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository),
) -> LiveService:
    return LiveService(
        analytics=analytics,
        video_storage=video_storage,
        detector=detector,
        buffer_manager=buffer_manager,
        snapshot_repository=snapshot_repository
    )

def get_offline_service(
    video: UploadFile = File(...),
    analytics: AnalyticsManager = Depends(get_analytics_manager),
    video_storage: VideoStorage = Depends(get_video_storage),
    detector: MediaPipeDetector = Depends(get_mp_detector),
    buffer_manager: BufferManager = Depends(get_buffer_manager),
) -> OfflineService:
    return OfflineService(
        video=video,
        analytics=analytics,
        video_storage=video_storage,
        detector=detector,
        buffer_manager=buffer_manager
    )
