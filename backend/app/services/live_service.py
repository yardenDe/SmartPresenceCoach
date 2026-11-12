
import av
from fastapi import UploadFile

from core.exceptions import (
    AppError,
    InvalidVideoError,
    NoLandmarksError,
    VisionProcessingError,
)
from core.logger import get_logger
from db.models.analysis import AudioFeatureRecord, Transcript, VideoMetric
from media.media_reader import MediaReader
from media.storage import Storage
from schemas.live import LiveResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


class LiveService:
    def __init__(
        self,
        storage: Storage,
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
            reader = MediaReader(video_path)
            video_chunk = next(reader.iter_video_chunks(), None)

            if video_chunk is None:
                self.logger.warning("event=live.video.empty session_id=%s", session_id)
                raise NoLandmarksError()

            audio_segments = reader.read_audio()
            audio = audio_segments[0] if audio_segments else None
            media_start = min(video_chunk.start_time, audio.start_time) if audio is not None else video_chunk.start_time
            offset = timestamp - media_start
            self.logger.debug(
                "event=live.media.ready session_id=%s frames=%s start_time=%.3f end_time=%.3f audio_segments=%s audio_selected=%s offset=%.3f",
                session_id, len(video_chunk.frames), video_chunk.start_time,
                video_chunk.end_time, len(audio_segments), audio is not None, offset,
            )

            visual = self.analysis_service.analyze_video(video_chunk.frames)
            if visual is None:
                self.logger.warning("event=live.video.no_landmarks session_id=%s", session_id)
                raise NoLandmarksError()

            records = [VideoMetric(
                session_id=session_id,
                start_time=video_chunk.start_time + offset,
                end_time=video_chunk.end_time + offset,
                **visual.model_dump(),
            )]
            audio_metrics = None

            if audio is not None:
                start_time = audio.start_time + offset
                end_time = audio.end_time + offset
                features = self.analysis_service.extract_audio(audio.data)
                audio_metrics = self.analysis_service.analyze_audio(features)
                records.append(AudioFeatureRecord(
                    session_id=session_id,
                    start_time=start_time,
                    end_time=end_time,
                    **features.to_dict(),
                ))


            scores = self.analysis_service.generate_scores(visual, audio_metrics)

            if scores is None:
                self.logger.warning("event=live.scores.empty session_id=%s", session_id)
                raise NoLandmarksError()

            self.logger.debug("event=live.persist.start session_id=%s records=%s", session_id, len(records))
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
            self.logger.exception("event=live.media.failed session_id=%s", session_id)
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
