from itertools import zip_longest

from fastapi import UploadFile

from core.exceptions import AppError, VisionProcessingError
from core.logger import get_logger
<<<<<<< Updated upstream
=======
from media.audio_extractor import AudioExtractor
from media.config import CHUNK_SECONDS
from media.frame_extractor import FrameExtractor
from media.storage import storage
>>>>>>> Stashed changes
from schemas.offline import OfflineResponse
from services.session_analysis_service import SessionAnalysisService
from video.video_storage import VideoStorage


class OfflineService:

    def __init__(
        self,
<<<<<<< Updated upstream
        video: UploadFile,
        video_storage: VideoStorage,
        session_analysis_service: SessionAnalysisService,
    ):
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
        self.logger = get_logger("app.services.offline")

        self.video_input = video
        self.video_path = None
        self.video_storage = video_storage
        self.session_analysis_service = session_analysis_service


    async def process(self, session_id: int) -> OfflineResponse:

        self.logger.info("event=offline.process.start file=%s", self.video_input.filename)
        self.video_path = await self.video_storage.save_temp(self.video_input)

        try:
<<<<<<< Updated upstream
            response = self.session_analysis_service.process_offline(
                video_path=self.video_path,
=======
            self.session_service.require_owned_session(user_id, session_id)
            video_path = await self.storage.save_temp(video)

            video_chunks = self.frame_extractor.get_chunks(video_path)
            audio_chunks = self.audio_extractor.stream(video_path)

            analyzed_count = 0

            for chunk_index, (frames, audio) in enumerate(
                zip_longest(video_chunks, audio_chunks),
                start=1,
            ):
                analysis = self.analysis_service.process(
                    frames=frames,
                    audio=audio,
                )
                visual = analysis.visual

                if visual is None:
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
>>>>>>> Stashed changes
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
            self.video_storage.delete(self.video_path)
            self.video_path = None
