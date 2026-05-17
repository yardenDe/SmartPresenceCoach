from typing import Any

from analytics.manager import AnalyticsManager
from core.exceptions import NoLandmarksError
from core.logger import get_logger
from services.session_buffer import SessionBuffer
from repositories.snapshot_repository import SnapshotRepository
from schemas.live import LiveResponse
from schemas.offline import OfflineResponse
from vision.config import CHUNK_SECONDS
from vision.mediapipe_detector import MediaPipeDetector
from vision.pipline import VisionPipeline


class SessionAnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        detector: MediaPipeDetector,
        session_buffer: SessionBuffer,
        snapshot_repository: SnapshotRepository,
    ):
        self.analytics = analytics
        self.detector = detector
        self.session_buffer = session_buffer
        self.snapshot_repository = snapshot_repository
        self.logger = get_logger("app.services.session_analysis")

    def process_live(self, video_path: str, session_id: int) -> LiveResponse:
        pipeline = VisionPipeline(self.detector)

        try:
            for chunk_index, landmarks_list in enumerate(
                pipeline.pipline(video_path=video_path),
                start=1,
            ):
                if not landmarks_list:
                    continue

                analysis = self._process_chunk(
                    session_id=session_id,
                    chunk_index=chunk_index,
                    landmarks_list=landmarks_list,
                )

                return LiveResponse(**self._build_live_response(analysis))

            raise NoLandmarksError()
        finally:
            pipeline.close()

    def process_offline(self, video_path: str, session_id: int) -> OfflineResponse:
        pipeline = VisionPipeline(self.detector)
        analyzed_count = 0

        try:
            for chunk_index, landmarks_list in enumerate(
                pipeline.pipline(video_path=video_path),
                start=1,
            ):
                if not landmarks_list:
                    continue

                self._process_chunk(
                    session_id=session_id,
                    chunk_index=chunk_index,
                    landmarks_list=landmarks_list,
                )

                analyzed_count += 1

            if analyzed_count == 0:
                raise NoLandmarksError()

            self.flush(session_id)

            return OfflineResponse(
                session_id=session_id,
                status="success",
            )
        finally:
            pipeline.close()

    def _process_chunk(
        self,
        session_id: int,
        chunk_index: int,
        landmarks_list: list[dict[str, Any]],
    ) -> dict[str, Any]:
        scores = {
            metric_name: float(score)
            for metric_name, score in self.analytics.run_full_analysis(landmarks_list).items()
            if score is not None
        }

        result = {
            "session_id": session_id,
            "chunk_index": chunk_index,
            "timestamp": self._timestamp_for_chunk(chunk_index),
            "frames_count": len(landmarks_list),
            "scores": scores,
        }

        self._handle_buffer(result)

        return result

    def _handle_buffer(self, result: dict[str, Any]) -> None:
        self.session_buffer.add(
            session_id=result["session_id"],
            snapshot={
                **result["scores"],
                "timestamp": result["timestamp"],
            },
        )

        if self.session_buffer.should_flush(result["session_id"]):
            self.flush(result["session_id"])

    def flush(self, session_id: int) -> None:
        snapshots = self.session_buffer.flush(session_id)

        self.snapshot_repository.create_snapshots(
            session_id=session_id,
            snapshots=snapshots,
        )

    def close_session(self, session_id: int) -> None:
        snapshots = self.session_buffer.close_session(session_id)

        self.snapshot_repository.create_snapshots(
            session_id=session_id,
            snapshots=snapshots,
        )

    def _build_live_response(self, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": result["session_id"],
            "result": self._build_analysis_response(result),
        }

    def _build_analysis_response(self, result: dict[str, Any]) -> dict[str, Any]:
        scores = result["scores"]

        return {
            "id": result["chunk_index"],
            "timestamp": result["timestamp"],
            "frames_analyzed": result["frames_count"],
            "overall": scores.get("overall", 0.0),
            "scores": scores,
        }

    def _timestamp_for_chunk(self, chunk_index: int) -> float:
        return float((chunk_index - 1) * CHUNK_SECONDS)
