from typing import Generator 

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 
from google import genai 
from sqlalchemy.orm import Session 
from groq import Groq 

from core.config import get_settings 
from core.logger import get_logger 
from core.exceptions import InvalidCredentialsError, LLMUnavailableError 
from core.security import SecurityService 
from db.db_manager import SessionLocal 
from audio.audio_pipeline import AudioPipeline
from audio.librosa_engine import LibrosaEngine
from analytics.audio.manager import AudioAnalyticsManager
from analytics.manager import AnalyticsManager 
from analytics.score_calculator import ScoreCalculator
from analytics.visual.manager import VisualAnalyticsManager
from llm.manager import Manager 
from repositories.session_repository import SessionRepository 
from repositories.snapshot_repository import SnapshotRepository 
from repositories.report_repository import ReportRepository 
from repositories.user_repository import UserRepository 
from reporting.pdf_renderer import ReportPdfRenderer
from services.auth_service import AuthService 
from infrastructure.email_engine import EmailEngine
from services.report_email_service import ReportEmailService
from services.live_service import LiveService 
from services.llm_service import LLMService 
from services.offline_service import OfflineService 
from services.report_service import ReportService 
from services.report_pdf_service import ReportPdfService 
from infrastructure.session_buffer import SessionBuffer
from services.analysis_service import AnalysisService
from services.session_service import SessionService 
from vision.mediapipe_detector import MediaPipeDetector 
from vision.vision_pipeline import VisionPipeline 
from media.audio_extractor import AudioExtractor
from media.storage import storage 
from audio.transcriber import Transcriber 
from media.frame_extractor import FrameExtractor 



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


def get_visual_analytics_manager() -> VisualAnalyticsManager:
    return VisualAnalyticsManager()


def get_audio_analytics_manager() -> AudioAnalyticsManager:
    return AudioAnalyticsManager()


def get_score_calculator() -> ScoreCalculator:
    return ScoreCalculator()


def get_analytics_manager(
    visual: VisualAnalyticsManager = Depends(get_visual_analytics_manager),
    audio: AudioAnalyticsManager = Depends(get_audio_analytics_manager),
    score_calculator: ScoreCalculator = Depends(get_score_calculator),
) -> AnalyticsManager:
    return AnalyticsManager(
        visual=visual,
        audio=audio,
        score_calculator=score_calculator,
    )


def get_storage() -> storage: 
    return storage() 

def get_frame_extractor() -> FrameExtractor: 
    return FrameExtractor() 


def get_audio_extractor() -> AudioExtractor:
    return AudioExtractor()


def get_librosa_engine() -> LibrosaEngine:
    return LibrosaEngine()


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


def get_vision_pipeline( 
    detector: MediaPipeDetector = Depends(get_mp_detector), 
) -> VisionPipeline: 
    return VisionPipeline(detector=detector) 


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
    session_service: SessionService = Depends(get_session_service), 
    snapshot_repository: SnapshotRepository = Depends(get_snapshot_repository), 
    report_repository: ReportRepository = Depends(get_report_repository), 
    score_calculator: ScoreCalculator = Depends(get_score_calculator),
) -> ReportService: 
    return ReportService( 
        session_service=session_service, 
        snapshot_repository=snapshot_repository, 
        report_repository=report_repository, 
        score_calculator=score_calculator,
    ) 


def get_email_engine() -> EmailEngine:
    return EmailEngine()


def get_report_pdf_renderer() -> ReportPdfRenderer:
    return ReportPdfRenderer()


def get_report_pdf_service(
    report_service: ReportService = Depends(get_report_service),
    pdf_renderer: ReportPdfRenderer = Depends(get_report_pdf_renderer),
) -> ReportPdfService:
    return ReportPdfService(
        report_service=report_service,
        pdf_renderer=pdf_renderer,
    )


def get_report_email_service(
    report_service: ReportService = Depends(get_report_service),
    pdf_renderer: ReportPdfRenderer = Depends(get_report_pdf_renderer),
    email_engine: EmailEngine = Depends(get_email_engine),
) -> ReportEmailService:
    return ReportEmailService(
        report_service=report_service,
        pdf_renderer=pdf_renderer,
        email_engine=email_engine,
    ) 


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


def get_audio_pipeline(
    engine: LibrosaEngine = Depends(get_librosa_engine),
    transcriber: Transcriber | None = Depends(get_transcriber),
) -> AudioPipeline:
    return AudioPipeline(engine=engine, transcriber=transcriber)


def get_analysis_service(
    analytics: AnalyticsManager = Depends(get_analytics_manager), 
    vision_pipeline: VisionPipeline = Depends(get_vision_pipeline),
    audio_pipeline: AudioPipeline = Depends(get_audio_pipeline),
) -> AnalysisService:
    return AnalysisService(
        analytics=analytics, 
        vision_pipeline=vision_pipeline,
        audio_pipeline=audio_pipeline,
    ) 


def get_live_service( 
    storage: storage = Depends(get_storage), 
    frame_extractor: FrameExtractor = Depends(get_frame_extractor),
    audio_extractor: AudioExtractor = Depends(get_audio_extractor),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    session_service: SessionService = Depends(get_session_service), 
) -> LiveService: 
    return LiveService( 
        storage=storage, 
        frame_extractor=frame_extractor,
        audio_extractor=audio_extractor,
        analysis_service=analysis_service,
        session_service=session_service,
    ) 

def get_offline_service( 
    storage: storage = Depends(get_storage), 
    frame_extractor: FrameExtractor = Depends(get_frame_extractor),
    audio_extractor: AudioExtractor = Depends(get_audio_extractor),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    session_service: SessionService = Depends(get_session_service), 
) -> OfflineService: 
    return OfflineService( 
        storage=storage, 
        frame_extractor=frame_extractor,
        audio_extractor=audio_extractor,
        analysis_service=analysis_service,
        session_service=session_service,
    ) 


