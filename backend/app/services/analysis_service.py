from typing import Any

from analytics.manager import AnalyticsManager
from media.config import CHUNK_SECONDS
from vision.vision_pipeline import VisionPipeline


class AnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        vision_pipeline: VisionPipeline,
    ):
        self.analytics = analytics
        self.vision_pipeline = vision_pipeline

    def process_chunk(
        self,
        chunk_frames: list[Any],
        chunk_index: int,
        timestamp_offset: float = 0.0,
    ) -> dict[str, Any] | None:

        landmarks_list = self.vision_pipeline.process(chunk_frames)

        if not landmarks_list:
            return None

        scores = {
            metric_name: float(score)
            for metric_name, score
            in self.analytics.run_full_analysis(landmarks_list).items()
            if score is not None
        }

        result = {
            "chunk_index": chunk_index,
            "timestamp": self._timestamp_for_chunk(
                chunk_index,
                timestamp_offset,
            ),
            "frames_count": len(landmarks_list),
            "scores": scores,
        }

        return result

    def _timestamp_for_chunk(
        self,
        chunk_index: int,
        timestamp_offset: float = 0.0,
    ) -> float:
        return float(
            timestamp_offset
            + (chunk_index - 1) * CHUNK_SECONDS
        )
