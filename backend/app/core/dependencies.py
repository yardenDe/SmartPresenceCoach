from typing import Generator 

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 
from google import genai 
from sqlalchemy.orm import Session 
from groq import Groq 

from core.settings import get_settings 
from core.logger import get_logger 
from core.exceptions import InvalidCredentialsError, LLMUnavailableError 
from core.security import SecurityService 
from db.db_manager import SessionLocal 
from extraction.extraction_manager import ExtractionManager
from extraction.audio.librosa_engine import LibrosaEngine
from analytics.audio.audio_analytics_manager import AudioAnalyticsManager
from analytics.analytics_manager import AnalyticsManager 
from analytics.score_calculator import ScoreCalculator
from analytics.visual.visual_analytics_manager import VisualAnalyticsManager
from llm.llm_manager import LLMManager 
from repositories.session_repository import SessionRepository 
from repositories.analysis_repository import AnalysisRepository
from repositories.report_repository import ReportRepository 
from repositories.user_repository import UserRepository 
from services.auth_service import AuthService 
from infrastructure.email_engine import EmailEngine
from services.live_service import LiveService 
from services.llm_service import LLMService 
from services.offline_service import OfflineService 
from services.report_service import ReportService 
from services.analysis_service import AnalysisService
from services.session_service import SessionService 
from extraction.video.mediapipe_detector import MediaPipeDetector 
from extraction.video.landmarks_extractor import LandmarksExtractor 
from media.storage import Storage 
from extraction.audio.transcriber import Transcriber 



security = HTTPBearer() 

logger = get_logger("app.core.dependencies") 

_detector_instance = None 
_llm_manager = None 
_transcriber = None 
_librosa_engine = None

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


def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def get_report_repository(db: Session = Depends(get_db)) -> ReportRepository: 
    return ReportRepository(db) 


def get_visual_analytics_manager() -> VisualAnalyticsManager:
    return VisualAnalyticsManager()


def get_audio_analytics_manager() -> AudioAnalyticsManager:
    return AudioAnalyticsManager()


def get_score_calculator() -> ScoreCalculator:
    return ScoreCalculator()


def get_analytics_manager(
    visual: VisualAnalyticsManager = Depends(get_visual_analytics_manager),
    audio: AudioAnalyticsManager = Depends(get_audio_analytics_manager),
) -> AnalyticsManager:
    return AnalyticsManager(
        visual=visual,
        audio=audio,
    )


def get_storage() -> Storage: 
    return Storage() 

def get_librosa_engine() -> LibrosaEngine:
    global _librosa_engine
    if _librosa_engine is None:
        engine = LibrosaEngine()
        engine.warmup()
        _librosa_engine = engine
    return _librosa_engine


def get_llm() -> LLMManager: 
    global _llm_manager 

    if _llm_manager is None: 
        settings = get_settings() 

        if not settings.LLM_API_KEY: 
            raise LLMUnavailableError() 

        _llm_manager = LLMManager( 
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
        settings = get_settings()
        _detector_instance = MediaPipeDetector(
            model_path=settings.MEDIAPIPE_MODEL_PATH,
            model_name=settings.POSE_LANDMARKER_MODEL,
            running_mode=settings.MEDIAPIPE_RUNNING_MODE,
        )
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


def get_vision_pipeline( 
    detector: MediaPipeDetector = Depends(get_mp_detector), 
) -> LandmarksExtractor: 
    return LandmarksExtractor(
        detector=detector,
    )


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


def get_session_service( 
    session_repository: SessionRepository = Depends(get_session_repository), 
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository),
) -> SessionService: 
    return SessionService( 
        session_repository=session_repository, 
        analysis_repository=analysis_repository,
    ) 


def get_report_service( 
    session_service: SessionService = Depends(get_session_service), 
    analysis_repository: AnalysisRepository = Depends(get_analysis_repository),
    report_repository: ReportRepository = Depends(get_report_repository), 
    score_calculator: ScoreCalculator = Depends(get_score_calculator),
) -> ReportService: 
    return ReportService( 
        session_service=session_service, 
        analysis_repository=analysis_repository,
        report_repository=report_repository, 
        score_calculator=score_calculator,
    ) 


def get_email_engine() -> EmailEngine:
    return EmailEngine()


def get_transcriber() -> Transcriber | None:
    global _transcriber

    if _transcriber is None:
        settings = get_settings()

        if not settings.GROQ_API_KEY:
            return None

        _transcriber = Transcriber(
            client=Groq(api_key=settings.GROQ_API_KEY),
            model=settings.TRANSCRIBER_MODEL,
        )

    return _transcriber


def get_extraction_manager(
    video_extractor: LandmarksExtractor = Depends(get_vision_pipeline),
    audio_engine: LibrosaEngine = Depends(get_librosa_engine),
    transcriber: Transcriber | None = Depends(get_transcriber),
) -> ExtractionManager:
    return ExtractionManager(
        video_extractor=video_extractor,
        audio_engine=audio_engine,
        transcriber=transcriber,
    )


def get_analysis_service(
    score_calculator: ScoreCalculator = Depends(get_score_calculator),
    analytics: AnalyticsManager = Depends(get_analytics_manager),
    extraction: ExtractionManager = Depends(get_extraction_manager),
) -> AnalysisService:
    return AnalysisService(
        score_calculator=score_calculator,
        analytics=analytics,
        extraction=extraction,
    )


def get_live_service( 
    storage: Storage = Depends(get_storage), 
    analysis_service: AnalysisService = Depends(get_analysis_service),
    session_service: SessionService = Depends(get_session_service), 
) -> LiveService: 
    return LiveService( 
        storage=storage, 
        analysis_service=analysis_service,
        session_service=session_service,
    ) 

def get_offline_service( 
    storage: Storage = Depends(get_storage), 
    analysis_service: AnalysisService = Depends(get_analysis_service),
    session_service: SessionService = Depends(get_session_service), 
) -> OfflineService: 
    return OfflineService( 
        storage=storage, 
        analysis_service=analysis_service,
        session_service=session_service,
    )
