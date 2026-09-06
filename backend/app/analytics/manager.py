from typing import Any

from analytics.audio.manager import AudioAnalyticsManager
from analytics.visual.manager import VisualAnalyticsManager
from schemas.analysis import Analysis, AudioFeatures


class AnalyticsManager:
    def __init__(
        self,
        visual: VisualAnalyticsManager,
        audio: AudioAnalyticsManager,
    ):
        self.visual = visual
        self.audio = audio

    def analyze(
        self,
        landmarks: list[dict[str, Any]] | None = None,
        audio_features: AudioFeatures | None = None,
    ) -> Analysis:
        return Analysis(
            visual=(
                self.visual.run_full_analysis(landmarks)
                if landmarks is not None
                else None
            ),
            audio=(
                self.audio.analyze(audio_features)
                if audio_features is not None
                else None
            ),
        )
