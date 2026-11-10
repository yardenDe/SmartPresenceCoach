import av
from fastapi import UploadFile

from core.exceptions import AppError, InvalidVideoError, NoLandmarksError, VisionProcessingError
from core.logger import get_logger
from db.models.analysis import AudioFeatureRecord, Transcript, VideoMetric
from media.media_reader import MediaReader
from media.storage import storage
from schemas.offline import OfflineResponse
from services.analysis_service import AnalysisService
from services.session_service import SessionService


VIDEO_CHUNK_SECONDS = 3


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

            records = []

            for chunk in reader.iter_video_chunks(VIDEO_CHUNK_SECONDS):
                visual = self.analysis_service.analyze_video([sample.data for sample in chunk])
                if visual is not None:
                    records.append(VideoMetric(
                        session_id=session_id,
                        start_time=chunk[0].start_time,
                        end_time=chunk[-1].end_time,
                        **visual.model_dump(),
                    ))

            audio = reader.read(video=False).audio

            if audio is not None:
                features = self.analysis_service.extract_audio(audio.data)
                records.append(AudioFeatureRecord(
                    session_id=session_id,
                    start_time=audio.start_time,
                    end_time=audio.end_time,
                    hop_length=512,
                    rms=features.rms.tolist(),
                    pitch=features.pitch.tolist(),
                    non_silent_intervals=features.non_silent_intervals.tolist(),
                    total_samples=features.total_samples,
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
                raise NoLandmarksError()
            
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
