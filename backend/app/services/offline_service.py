from fastapi import UploadFile

from core.exceptions import AppError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
from media.config import CHUNK_SECONDS
from media.frame_extractor import FrameExtractor
from media.storage import storage
from schemas.offline import OfflineResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


class OfflineService:
    def __init__(
        self,
        storage: storage,
        frame_extractor: FrameExtractor,
        analysis_service: AnalysisService,
        session_service: SessionService,
    ):
        self.storage = storage
        self.frame_extractor = frame_extractor
        self.analysis_service = analysis_service
        self.session_service = session_service
        self.logger = get_logger("app.services.offline")

    async def process(
        self,
        video: UploadFile,
        user_id: int,
        session_id: int,
    ) -> OfflineResponse:

        self.logger.info(
            "event=offline.process.start file=%s",
            video.filename,
        )

        video_path = None

        try:
            self.session_service.require_owned_session(user_id, session_id)
            video_path = await self.storage.save_temp(video)

            analyzed_count = 0

            for chunk_index, chunk_frames in enumerate(
                self.frame_extractor.get_chunks(video_path),
                start=1,
            ):
                analysis = self.analysis_service.process_chunk(
                    chunk_frames=chunk_frames,
                )

                if analysis is None:
                    continue

                self.session_service.add_analysis(
                    session_id=session_id,
                    timestamp=float((chunk_index - 1) * CHUNK_SECONDS),
                    analysis=analysis,
                )
                analyzed_count += 1

            if analyzed_count == 0:
                raise NoLandmarksError()

            self.session_service.end(user_id, session_id)

            response = OfflineResponse(
                session_id=session_id,
                status="success",
            )

            self.logger.info(
                "event=offline.process.done session_id=%s chunks=%s",
                session_id,
                analyzed_count,
            )

            return response

        except AppError:
            raise

        except Exception:
            self.logger.exception(
                "event=offline.process.failed session_id=%s",
                session_id,
            )
            raise VisionProcessingError()

        finally:
            if video_path:
                self.storage.delete(video_path)
