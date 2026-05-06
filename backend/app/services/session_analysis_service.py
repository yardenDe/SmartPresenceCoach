from typing import Any

from analytics.manager import AnalyticsManager
from core.exceptions import NoLandmarksError
from core.logger import get_logger
from db.buffer_manager import BufferManager
from repositories.snapshot_repository import SnapshotRepository
from schemas.analysis import AnalysisResponse
from schemas.live import LiveResponse
from schemas.offline import OfflineResponse
from vision.mediapipe_detector import MediaPipeDetector
from vision.pipline import VisionPipeline


class SessionAnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        detector: MediaPipeDetector,
        buffer_manager: BufferManager,
        snapshot_repository: SnapshotRepository,
    ):
        self.analytics = analytics
        self.detector = detector
        self.buffer_manager = buffer_manager
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
        chunk_responses = []
        total_overall = 0.0
        analyzed_count = 0

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

                analysis_response = self._build_analysis_response(analysis)
                chunk_responses.append(analysis_response)

                total_overall += analysis_response["overall_score"]
                analyzed_count += 1

            if analyzed_count == 0:
                raise NoLandmarksError()

            self.flush(session_id)

            return OfflineResponse(
                session_id=session_id,
                overall_score=total_overall / analyzed_count,
                results=[AnalysisResponse(**chunk) for chunk in chunk_responses],
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
        self.buffer_manager.add(
            session_id=result["session_id"],
            snapshot={
                **result["scores"],
                "timestamp": result["timestamp"],
            },
        )

        if self.buffer_manager.should_flush(result["session_id"]):
            self.flush(result["session_id"])

    def flush(self, session_id: int) -> None:
        snapshots = self.buffer_manager.flush(session_id)

        for snapshot in snapshots:
            self.snapshot_repository.create_snapshot(
                session_id=session_id,
                timestamp=snapshot.get("timestamp", 0.0),
                scores=snapshot,
            )

    def close_session(self, session_id: int) -> None:
        snapshots = self.buffer_manager.close_session(session_id)

        for snapshot in snapshots:
            self.snapshot_repository.create_snapshot(
                session_id=session_id,
                timestamp=snapshot.get("timestamp", 0.0),
                scores=snapshot,
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
            "overall_score": scores.get("overall", 0.0),
            "scores": scores,
        }

    def _timestamp_for_chunk(self, chunk_index: int) -> float:
        return float((chunk_index - 1) * 3)
