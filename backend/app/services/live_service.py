
import av
from fastapi import UploadFile

from core.exceptions import (
    AppError,
    InvalidVideoError,
    NoLandmarksError,
    VisionProcessingError,
)
from core.logger import get_logger
from media.media_reader import MediaReader
from media.storage import storage
from schemas.live import LiveResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


class LiveService:
    def __init__(
        self,
        storage: storage,
        analysis_service: AnalysisService,
        session_service: SessionService,
    ):
        self.storage = storage
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
            media = MediaReader(video_path).read()

            if not media.video:
                raise NoLandmarksError()

            offset = timestamp - media.start_time

            video_record = self.analysis_service.analyze_video(
                session_id,
                media.video[0].start_time + offset,
                media.video[-1].end_time + offset,
                [sample.data for sample in media.video],
            )

            if video_record is None:
                raise NoLandmarksError()

            records = [video_record]
            audio_record = None

            if media.audio is not None:
                audio_record = self.analysis_service.analyze_audio(
                    session_id,
                    media.audio.start_time + offset,
                    media.audio.end_time + offset,
                    media.audio.data,
                )

                if audio_record is not None:
                    records.append(audio_record)

                if self.analysis_service.transcription_enabled:
                    transcript_record = self.analysis_service.transcribe(
                        session_id,
                        media.audio.start_time + offset,
                        media.audio.end_time + offset,
                        media.audio.data,
                    )

                    if transcript_record is not None:
                        records.append(transcript_record)

            scores = self.analysis_service.generate_scores(
                video_record,
                audio_record,
            )

            if scores is None:
                raise NoLandmarksError()

            self.session_service.save_analysis_records(records)

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

        except av.FFmpegError as error:
            raise InvalidVideoError() from error

        except Exception:
            self.logger.exception(
                "event=live.process.failed session_id=%s",
                session_id,
            )
            raise VisionProcessingError()

        finally:
            if video_path:
                self.storage.delete(video_path)
