from fastapi import UploadFile

from core.exceptions import AppError, VisionProcessingError
from core.logger import get_logger
from schemas.offline import OfflineResponse
from services.session_analysis_service import SessionAnalysisService
from media.storage import storage


class OfflineService:

    def __init__(
        self,
        video: UploadFile,
        storage: storage,
        session_analysis_service: SessionAnalysisService,
    ):
        self.logger = get_logger("app.services.offline")

        self.video_input = video
        self.video_path = None
        self.storage = storage
        self.session_analysis_service = session_analysis_service


    async def process(self, session_id: int) -> OfflineResponse:

        self.logger.info("event=offline.process.start file=%s", self.video_input.filename)
        self.video_path = await self.storage.save_temp(self.video_input)

        try:
            response = self.session_analysis_service.process_offline(
                video_path=self.video_path,
                session_id=session_id,
            )

            self.logger.info("event=offline.process.done status=%s", response.status)
            return response

        except AppError:
            raise
        except Exception:
            self.logger.exception("event=offline.process.failed")
            raise VisionProcessingError()
        finally:
            self.close()

    
    def close(self) -> None:
        if self.video_path:
            self.storage.delete(self.video_path)
            self.video_path = None
