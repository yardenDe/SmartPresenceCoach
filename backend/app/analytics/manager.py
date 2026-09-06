from typing import Any

from analytics.audio.manager import AudioAnalyticsManager
from analytics.score_calculator import ScoreCalculator
from analytics.visual.manager import VisualAnalyticsManager
from schemas.analysis import Analysis, AudioFeatures, Scores


class AnalyticsManager:
    def __init__(
        self,
        visual: VisualAnalyticsManager,
        audio: AudioAnalyticsManager,
        score_calculator: ScoreCalculator,
    ):
        self.visual = visual
        self.audio = audio
        self.score_calculator = score_calculator

    def analyze(
        self,
        landmarks: list[dict[str, Any]] | None = None,
        audio_features: AudioFeatures | None = None,
    ) -> Analysis:
        return Analysis(
            visual=(
                self.visual.analyze(landmarks)
                if landmarks is not None
                else None
            ),
            audio=(
                self.audio.analyze(audio_features)
                if audio_features is not None
                else None
            ),
        )

    def generate_scores(self, analysis: Analysis) -> Scores | None:
        return self.score_calculator.calculate(
            visual=analysis.visual,
            audio=analysis.audio,
        )
