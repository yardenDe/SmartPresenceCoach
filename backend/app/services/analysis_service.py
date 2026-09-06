from typing import Any

import numpy as np

from analytics.manager import AnalyticsManager
from audio.audio_pipeline import AudioPipeline
from core.logger import get_logger
from schemas.analysis import Analysis, Scores
from vision.vision_pipeline import VisionPipeline

logger = get_logger("app.services.analysis")


class AnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        vision_pipeline: VisionPipeline,
        audio_pipeline: AudioPipeline | None = None,
    ):
        self.analytics = analytics
        self.vision_pipeline = vision_pipeline
        self.audio_pipeline = audio_pipeline

    def process(
        self,
        frames: list[Any] | None = None,
        audio: np.ndarray | None = None,
    ) -> Analysis:
        landmarks = None
        audio_features = None

        if frames is not None:
            landmarks = self.vision_pipeline.process(frames) or None

        if audio is None:
            logger.debug("event=analysis.audio.missing")
        elif self.audio_pipeline is None:
            logger.warning("event=analysis.audio.pipeline_unavailable")
        else:
            audio_features = self.audio_pipeline.process(audio)

        result = self.analytics.analyze(
            landmarks=landmarks,
            audio_features=audio_features,
        )

        logger.debug(
            "event=analysis.process.done visual=%s audio=%s",
            result.visual is not None,
            result.audio is not None,
        )

        return result

    def generate_scores(self, analysis: Analysis) -> Scores | None:
        return self.analytics.generate_scores(analysis)
