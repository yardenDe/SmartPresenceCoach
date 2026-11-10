
import av
from fastapi import UploadFile

from core.exceptions import AppError, InvalidVideoError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
from media.media_reader import MediaReader
from media.storage import storage
from schemas.offline import OfflineResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


VIDEO_CHUNK_SECONDS = 3
AUDIO_CHUNK_SECONDS = 3
TRANSCRIPT_CHUNK_SECONDS = 3


class OfflineService:
    def __init__(
        self,
        storage: storage,
        analysis_service: AnalysisService,
        session_service: SessionService,
    ):
        self.storage = storage
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
            reader = MediaReader(video_path)

            video_records = []

            for chunk in reader.iter_video_chunks(VIDEO_CHUNK_SECONDS):
                record = self.analysis_service.analyze_video(
                    session_id,
                    chunk[0].start_time,
                    chunk[-1].end_time,
                    [sample.data for sample in chunk],
                )
                if record is not None:
                    video_records.append(record)

            audio_records = []

            for chunk in reader.iter_audio_chunks(AUDIO_CHUNK_SECONDS):
                record = self.analysis_service.analyze_audio(
                    session_id,
                    chunk.start_time,
                    chunk.end_time,
                    chunk.data,
                )
                if record is not None:
                    audio_records.append(record)

            if not video_records and not audio_records:
                raise NoLandmarksError()

            records = video_records + audio_records

            if self.analysis_service.transcription_enabled:
                for chunk in reader.iter_audio_chunks(TRANSCRIPT_CHUNK_SECONDS):
                    record = self.analysis_service.transcribe(
                        session_id,
                        chunk.start_time,
                        chunk.end_time,
                        chunk.data,
                    )
                    if record is not None:
                        records.append(record)

            self.session_service.save_analysis_records(records)
            self.session_service.end(user_id, session_id)

            response = OfflineResponse(
                session_id=session_id,
                status="success",
            )

            self.logger.info(
                "event=offline.process.done session_id=%s records=%s",
                session_id,
                len(records),
            )

            return response

        except AppError:
            raise

        except av.FFmpegError as error:
            raise InvalidVideoError() from error

        except Exception:
            self.logger.exception(
                "event=offline.process.failed session_id=%s",
                session_id,
            )
            raise VisionProcessingError()

        finally:
            if video_path:
                self.storage.delete(video_path)
