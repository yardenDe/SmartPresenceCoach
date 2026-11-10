
import numpy as np

from analytics.manager import AnalyticsManager
from analytics.score_calculator import ScoreCalculator
from extraction.manager import ExtractionManager
from schemas.analysis import AudioFeatures, AudioMetrics, Scores, VisualMetrics


class AnalysisService:
    def __init__(
        self,
        analytics: AnalyticsManager,
        score_calculator: ScoreCalculator,
        extraction: ExtractionManager,
    ):
        self.analytics = analytics
        self.extraction = extraction
        self.score_calculator = score_calculator

    def analyze_video(self, frames: list[np.ndarray]) -> VisualMetrics | None:
        landmarks = self.extraction.extract_video(frames) or None
        return self.analytics.analyze(landmarks=landmarks).visual

    def analyze_audio(self, audio: np.ndarray) -> AudioMetrics | None:
        features = self.extraction.extract_audio(audio)
        return self.analytics.analyze(audio_features=features).audio

    def extract_audio(self, audio: np.ndarray) -> AudioFeatures:
        return self.extraction.extract_audio(audio)

    def transcribe(self, audio: np.ndarray) -> str | None:
        return self.extraction.transcribe(audio)

    def generate_scores(
        self,
        video: VisualMetrics | None = None,
        audio: AudioMetrics | None = None,
    ) -> Scores | None:
        return self.score_calculator.calculate(video, audio)
