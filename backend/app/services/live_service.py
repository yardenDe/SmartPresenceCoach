from typing import Any

from fastapi import UploadFile

from analytics.manager import AnalyticsManager
from core.exceptions import AppError, VisionProcessingError
from core.logger import get_logger
from vision.mediapipe_detector import MediaPipeDetector
from vision.pipline import VisionPipeline
from vision.video_storage import VideoStorage


class LiveService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        video_storage: VideoStorage,
        detector: MediaPipeDetector,
    ):
        self.analytics = analytics
        self.video_storage = video_storage
        self.detector = detector
        self.video_path = None
        self.vision_pipeline = None
        self.logger = get_logger("app.services.live")

    async def process(self, video: UploadFile, session_id: int) -> dict[str, Any]:
        self.logger.info("event=live.process.start session_id=%s file=%s", session_id, video.filename)

        try:
            self.video_path = await self.video_storage.save_temp(video)
            landmarks = self._get_first_chunk(self.video_path)
            scores = self._analyze(landmarks)
            response = self._build_response(session_id, scores)

            self.logger.info(
                "event=live.process.done session_id=%s frames=%s overall=%.2f",
                session_id,
                len(landmarks),
                response["overall_score"],
            )
            return response
        except AppError:
            raise
        except Exception:
            self.logger.exception("event=live.process.failed session_id=%s", session_id)
            raise VisionProcessingError()
        finally:
            self.close()

    def _get_first_chunk(self, video_path: str) -> list[dict[str, Any]]:
        self.vision_pipeline = VisionPipeline(self.detector)

        for chunk_index, landmarks in enumerate(self.vision_pipeline.pipline(video_path=video_path), start=1):
            if landmarks:
                self.logger.info(
                    "event=live.chunk.ready chunk=%s frames=%s",
                    chunk_index,
                    len(landmarks),
                )
                return landmarks

        self.logger.warning("event=live.chunk.empty")
        return []

    def _analyze(self, landmarks: list[dict[str, Any]]) -> dict[str, float]:
        if not landmarks:
            self.logger.warning("event=live.analysis.empty")
            return {
                "focus": 0.0,
                "vitality": 0.0,
                "posture": 0.0,
                "presence": 0.0,
                "composure": 0.0,
                "overall": 0.0,
            }

        return self.analytics.run_full_analysis(landmarks)

    def _build_response(self, session_id: int, scores: dict[str, float]) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "overall_score": scores.get("overall", 0.0),
            "focus": scores.get("focus", 0.0),
            "vitality": scores.get("vitality", 0.0),
            "posture": scores.get("posture", 0.0),
            "presence": scores.get("presence", 0.0),
            "composure": scores.get("composure", 0.0),
            "delivery": None,
        }

    def close(self) -> None:
        if self.vision_pipeline:
            self.vision_pipeline.close()
            self.vision_pipeline = None

        if self.video_path:
            self.video_storage.delete(self.video_path)
            self.video_path = None
