from typing import Any
import numpy as np

from analytics.manager import AnalyticsManager
from analytics.score_calculator import ScoreCalculator
from audio.audio_pipeline import AudioPipeline
from core.logger import get_logger
from models.snapshot import Snapshot
from schemas.analysis import Scores
from vision.vision_pipeline import VisionPipeline

logger = get_logger("app.services.analysis")


class AnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        vision_pipeline: VisionPipeline,
        score_calculator: ScoreCalculator,
        audio_pipeline: AudioPipeline | None = None,
    ):
        self.analytics = analytics
        self.vision_pipeline = vision_pipeline
        self.audio_pipeline = audio_pipeline
        self.score_calculator = score_calculator

    def process(
        self,
        session_id: int,
        timestamp: float,
        frames: list[Any] | None = None,
        audio: np.ndarray | None = None,
    ) -> Snapshot | None:
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

        if result.visual is None and result.audio is None:
            return None

        return Snapshot(
            session_id=session_id,
            timestamp=timestamp,
            **(result.visual.model_dump() if result.visual else {}),
            **(result.audio.model_dump() if result.audio else {}),
        )

    def generate_scores(self, snapshot: Snapshot) -> Scores | None:
        return self.score_calculator.calculate(snapshot)
