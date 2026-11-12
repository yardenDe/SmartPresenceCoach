import av
from fastapi import UploadFile

from analytics.config import ANALYSIS_WINDOW_SECONDS
from core.exceptions import AppError, InvalidVideoError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
from db.models.analysis import AudioFeatureRecord, Transcript, VideoMetric
from media.media_reader import MediaReader
from media.storage import Storage
from schemas.offline import OfflineResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService



class OfflineService:
    def __init__(
        self,
        storage: Storage,
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

            records = []

            for chunk in reader.iter_video_chunks(ANALYSIS_WINDOW_SECONDS):
                self.logger.debug(
                    "event=offline.video.chunk session_id=%s start_time=%.3f end_time=%.3f frames=%s",
                    session_id, chunk.start_time, chunk.end_time, len(chunk.frames),
                )
                visual = self.analysis_service.analyze_video(chunk.frames)
                self.logger.debug(
                    "event=offline.video.analyzed session_id=%s start_time=%.3f has_metrics=%s",
                    session_id, chunk.start_time, visual is not None,
                )
                if visual is not None:
                    records.append(VideoMetric(
                        session_id=session_id,
                        start_time=chunk.start_time,
                        end_time=chunk.end_time,
                        **visual.model_dump(),
                    ))

            for audio in reader.read_audio():
                self.logger.debug(
                    "event=offline.audio.segment session_id=%s start_time=%.3f end_time=%.3f samples=%s",
                    session_id, audio.start_time, audio.end_time, audio.data.size,
                )
                features = self.analysis_service.extract_audio(audio.data)
                records.append(AudioFeatureRecord(
                    session_id=session_id,
                    start_time=audio.start_time,
                    end_time=audio.end_time,
                    **features.to_dict(),
                ))
                text = self.analysis_service.transcribe(audio.data)
                if text is not None:
                    records.append(Transcript(
                        session_id=session_id,
                        start_time=audio.start_time,
                        end_time=audio.end_time,
                        transcript=text,
                    ))

            if not records:
                self.logger.warning("event=offline.analysis.empty session_id=%s", session_id)
                raise NoLandmarksError()
            
            self.logger.debug("event=offline.persist.start session_id=%s records=%s", session_id, len(records))
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
            self.logger.exception("event=offline.media.failed session_id=%s", session_id)
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
