from fastapi import UploadFile

from core.exceptions import AppError, VisionProcessingError
from core.logger import get_logger
<<<<<<< Updated upstream
=======
from media.audio_extractor import AudioExtractor
from media.frame_extractor import FrameExtractor
from media.storage import storage
>>>>>>> Stashed changes
from schemas.live import LiveResponse
from services.session_analysis_service import SessionAnalysisService
from video.video_storage import VideoStorage


class LiveService:
    def __init__(
        self,
<<<<<<< Updated upstream
        video_storage: VideoStorage,
        session_analysis_service: SessionAnalysisService,
    ):
        self.video_storage = video_storage
        self.video_path = None
        self.session_analysis_service = session_analysis_service

=======
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
>>>>>>> Stashed changes
        self.logger = get_logger("app.services.live")

    async def process(self, video: UploadFile, session_id: int, timestamp: float = 0.0) -> LiveResponse:
        self.logger.info(
            "event=live.process.start session_id=%s timestamp=%.2f file=%s",
            session_id,
            timestamp,
            video.filename,
        )

        try:
<<<<<<< Updated upstream
            self.video_path = await self.video_storage.save_temp(video)
            response = self.session_analysis_service.process_live(
                video_path=self.video_path,
                session_id=session_id,
                timestamp_offset=timestamp,
=======
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

            visual = analysis.visual

            if visual is None:
                raise NoLandmarksError()

            self.session_service.add_analysis(
                session_id=session_id,
                timestamp=timestamp,
                analysis=analysis,
            )

            self.logger.info(
                "event=live.process.done session_id=%s overall=%.2f",
                session_id,
                visual.overall,
            )

            return LiveResponse(
                session_id=session_id,
                timestamp=timestamp,
                analysis=analysis,
>>>>>>> Stashed changes
            )

            self.logger.info(
                "event=live.process.done session_id=%s frames=%s overall=%.2f",
                session_id,
                response.result.frames_analyzed,
                response.result.overall,
            )
            return response
        except AppError:
            raise
        except Exception:
            self.logger.exception("event=live.process.failed session_id=%s", session_id)
            raise VisionProcessingError()
        finally:
            self.close()

    def close(self) -> None:
        if self.video_path:
            self.video_storage.delete(self.video_path)
            self.video_path = None
