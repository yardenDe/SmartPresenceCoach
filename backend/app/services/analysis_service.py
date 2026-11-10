import numpy as np

from analytics.analytics_manager import AnalyticsManager
from analytics.config import AudioMetrics, Scores, VideoMetrics
from analytics.score_calculator import ScoreCalculator
from extraction.audio.config import AudioFeatures
from extraction.extraction_manager import ExtractionManager


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

    def analyze_video(self, frames: list[np.ndarray]) -> VideoMetrics | None:
        landmarks = self.extraction.extract_video(frames)
        return self.analytics.analyze_video(landmarks) if landmarks else None

    def analyze_audio(self, features: AudioFeatures) -> AudioMetrics:
        return self.analytics.analyze_audio(features)

    def extract_audio(self, audio: np.ndarray) -> AudioFeatures:
        return self.extraction.extract_audio(audio)

    def transcribe(self, audio: np.ndarray) -> str | None:
        return self.extraction.transcribe(audio)

    def generate_scores(
        self,
        video: VideoMetrics | None = None,
        audio: AudioMetrics | None = None,
    ) -> Scores | None:
        return self.score_calculator.calculate(video, audio)
