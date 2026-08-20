from fastapi import UploadFile

from core.exceptions import AppError, VisionProcessingError
from core.logger import get_logger
from schemas.live import LiveResponse
from services.session_analysis_service import SessionAnalysisService
from video.video_storage import VideoStorage


class LiveService:
    def __init__(
        self,
        video_storage: VideoStorage,
        session_analysis_service: SessionAnalysisService,
    ):
        self.video_storage = video_storage
        self.video_path = None
        self.session_analysis_service = session_analysis_service

        self.logger = get_logger("app.services.live")

    async def process(self, video: UploadFile, session_id: int, timestamp: float = 0.0) -> LiveResponse:
        self.logger.info(
            "event=live.process.start session_id=%s timestamp=%.2f file=%s",
            session_id,
            timestamp,
            video.filename,
        )

        try:
            self.video_path = await self.video_storage.save_temp(video)
            response = self.session_analysis_service.process_live(
                video_path=self.video_path,
                session_id=session_id,
                timestamp_offset=timestamp,
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
