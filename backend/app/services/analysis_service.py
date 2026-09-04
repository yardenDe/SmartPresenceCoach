from typing import Any

from analytics.manager import AnalyticsManager
from schemas.analysis import VisualAnalysis
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
    ) -> VisualAnalysis | None:

        landmarks_list = self.vision_pipeline.process(chunk_frames)

        if not landmarks_list:
            return None

        return self.analytics.analyze_visual(landmarks_list)
