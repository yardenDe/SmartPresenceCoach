from fastapi import UploadFile

from core.exceptions import AppError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
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
        analysis_service: AnalysisService,
        session_service: SessionService,
    ):
        self.storage = storage
        self.frame_extractor = frame_extractor
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
            self.session_service.require_owned_session(user_id, session_id)
            video_path = await self.storage.save_temp(video)

            for chunk_index, chunk_frames in enumerate(
                self.frame_extractor.get_chunks(video_path),
                start=1,
            ):
                analysis = self.analysis_service.process_chunk(
                    chunk_frames=chunk_frames,
                    chunk_index=chunk_index,
                    timestamp_offset=timestamp,
                )

                if analysis is None:
                    continue

                self.session_service.add_analysis(session_id, analysis)
                response = self._build_response(session_id, analysis)

                self.logger.info(
                    "event=live.process.done session_id=%s frames=%s overall=%.2f",
                    session_id,
                    response.result.frames_analyzed,
                    response.result.overall,
                )

                return response

            raise NoLandmarksError()

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

    def _build_response(self, session_id: int, analysis: dict) -> LiveResponse:
        return LiveResponse(
            session_id=session_id,
            result={
                "id": analysis["chunk_index"],
                "timestamp": analysis["timestamp"],
                "frames_analyzed": analysis["frames_count"],
                "overall": analysis["scores"].get("overall", 0.0),
                "scores": analysis["scores"],
            },
        )
