
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

            visual = self.analysis_service.analyze_video([sample.data for sample in media.video])
            if visual is None:
                raise NoLandmarksError()

            records = [VideoMetric(
                session_id=session_id,
                start_time=media.video[0].start_time + offset,
                end_time=media.video[-1].end_time + offset,
                **visual.model_dump(),
            )]
            audio_metrics = None

            if media.audio is not None:
                start_time = media.audio.start_time + offset
                end_time = media.audio.end_time + offset
                audio_metrics = self.analysis_service.analyze_audio(media.audio.data)
                features = self.analysis_service.extract_audio(media.audio.data)
                records.append(AudioFeatureRecord(
                    session_id=session_id,
                    start_time=start_time,
                    end_time=end_time,
                    hop_length=512,
                    rms=features.rms.tolist(),
                    pitch=features.pitch.tolist(),
                    non_silent_intervals=features.non_silent_intervals.tolist(),
                    total_samples=features.total_samples,
                ))

                text = self.analysis_service.transcribe(media.audio.data)
                if text is not None:
                    records.append(Transcript(
                        session_id=session_id, start_time=start_time, end_time=end_time, transcript=text
                    ))

            scores = self.analysis_service.generate_scores(visual, audio_metrics)

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
