from fastapi import UploadFile

from core.exceptions import AppError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
from media.audio_extractor import AudioExtractor
from media.frame_extractor import FrameExtractor
from media.storage import storage
from schemas.live import LiveResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


class LiveService:
    def __init__(
        self,
        storage: storage,
        frame_extractor: FrameExtractor,
        audio_extractor: AudioExtractor,
        analysis_service: AnalysisService,
        session_service: SessionService,
    ):
        self.storage = storage
        self.frame_extractor = frame_extractor
        self.audio_extractor = audio_extractor
        self.analysis_service = analysis_service
        self.session_service = session_service
        self.logger = get_logger("app.services.live")

    async def process(
        self,
        video: UploadFile,
        user_id: int,
        session_id: int,
        timestamp: float = 0.0,
    ) -> LiveResponse:

        self.logger.info(
            "event=live.process.start session_id=%s timestamp=%.2f file=%s",
            session_id,
            timestamp,
            video.filename,
        )

        video_path = None

        try:
            self.session_service.require_owned_session(
                user_id,
                session_id,
            )

            video_path = await self.storage.save_temp(video)

            frames = self.frame_extractor.extract(video_path)
            audio = self.audio_extractor.extract(video_path)

            analysis = self.analysis_service.process(
                frames=frames,
                audio=audio,
            )

            scores = self.analysis_service.generate_scores(analysis)

            if analysis.visual is None or scores is None:
                raise NoLandmarksError()

            self.session_service.add_analysis(
                session_id=session_id,
                timestamp=timestamp,
                analysis=analysis,
            )

            self.logger.info(
                "event=live.process.done session_id=%s overall=%.2f",
                session_id,
                scores.overall,
            )

            return LiveResponse(
                session_id=session_id,
                timestamp=timestamp,
                scores=scores,
            )

        except AppError:
            raise

        except Exception:
            self.logger.exception(
                "event=live.process.failed session_id=%s",
                session_id,
            )
            raise VisionProcessingError()

        finally:
            if video_path:
                self.storage.delete(video_path)
