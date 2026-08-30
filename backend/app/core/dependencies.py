from typing import Generator

from fastapi import Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google import genai
from sqlalchemy.orm import Session
from groq import Groq

from core.config import get_settings
from core.logger import get_logger
from core.exceptions import InvalidCredentialsError, LLMUnavailableError
from core.security import SecurityService
from db.db_manager import SessionLocal
from analytics.manager import AnalyticsManager
from llm.manager import Manager
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from repositories.report_repository import ReportRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.email_engine import EmailEngine
from services.email_service import EmailService
from services.live_service import LiveService
from services.llm_service import LLMService
from services.offline_service import OfflineService
from services.report_service import ReportService
from services.report_pdf_service import ReportPdfService
from services.session_buffer import SessionBuffer
from services.session_analysis_service import SessionAnalysisService
from services.session_service import SessionService
from vision.mediapipe_detector import MediaPipeDetector
from video.video_storage import VideoStorage
from audio.transcriber import Transcriber


security = HTTPBearer()

logger = get_logger("app.core.dependencies")

_detector_instance = None
_session_buffer = SessionBuffer()
_llm_manager = None
_transcriber = None

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


def get_report_repository(db: Session = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)


def get_analytics_manager() -> AnalyticsManager:
    return AnalyticsManager()


def get_video_storage() -> VideoStorage:
    return VideoStorage()


def get_llm() -> Manager:
    global _llm_manager

    if _llm_manager is None:
        settings = get_settings()

        if not settings.LLM_API_KEY:
            raise LLMUnavailableError()

        _llm_manager = Manager(
            client=genai.Client(api_key=settings.LLM_API_KEY),
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
        )

    return _llm_manager



def get_llm_service() -> LLMService | None:
    try:
        return LLMService(manager=get_llm())
    except LLMUnavailableError:
        logger.warning("event=llm.unavailable")
        return None


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


def get_session_buffer() -> SessionBuffer:
    return _session_buffer


def get_session_service(
    session_repository: SessionRepository = Depends(get_session_repository),
    session_buffer: SessionBuffer = Depends(get_session_buffer),
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository),
) -> SessionService:
    return SessionService(
        session_repository=session_repository,
        session_buffer=session_buffer,
        snapshot_repository=snapshot_repository,
    )


def get_report_service(
    session_repository: SessionRepository = Depends(get_session_repository),
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
) -> ReportService:
    return ReportService(
        session_repository=session_repository,
        snapshot_repository=snapshot_repository,
        report_repository=report_repository,
    )


def get_email_engine() -> EmailEngine:
    return EmailEngine()


def get_email_service(
    session_repository: SessionRepository = Depends(get_session_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
    email_engine: EmailEngine = Depends(get_email_engine),
) -> EmailService:
    return EmailService(
        session_repository=session_repository,
        report_repository=report_repository,
        email_engine=email_engine,
    )


def get_report_pdf_service(
    session_repository: SessionRepository = Depends(get_session_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
) -> ReportPdfService:
    return ReportPdfService(
        session_repository=session_repository,
        report_repository=report_repository,
    )


def get_session_analysis_service(
    analytics: AnalyticsManager = Depends(get_analytics_manager),
    detector: MediaPipeDetector = Depends(get_mp_detector),
    session_buffer: SessionBuffer = Depends(get_session_buffer),
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository),
) -> SessionAnalysisService:
    return SessionAnalysisService(
        analytics=analytics,
        detector=detector,
        session_buffer=session_buffer,
        snapshot_repository=snapshot_repository,
    )


def get_live_service(
    video_storage: VideoStorage = Depends(get_video_storage),
    session_analysis_service: SessionAnalysisService = Depends(get_session_analysis_service),
) -> LiveService:
    return LiveService(
        video_storage=video_storage,
        session_analysis_service=session_analysis_service,
    )

def get_offline_service(
    video: UploadFile = File(...),
    video_storage: VideoStorage = Depends(get_video_storage),
    session_analysis_service: SessionAnalysisService = Depends(get_session_analysis_service),
) -> OfflineService:
    return OfflineService(
        video=video,
        video_storage=video_storage,
        session_analysis_service=session_analysis_service,
    )


def get_transcriber() -> Transcriber:
    global _transcriber

    if _transcriber is None:
        settings = get_settings()

        _transcriber = Transcriber(
            client=Groq(api_key=settings.GROQ_API_KEY),
            model=settings.TRANSCRIBER_MODEL,
        )

    return _transcriber