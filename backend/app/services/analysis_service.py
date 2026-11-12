import numpy as np

from analytics.analytics_manager import AnalyticsManager
from analytics.config import AudioMetrics, Scores, VideoMetrics
from analytics.score_calculator import ScoreCalculator
from extraction.audio.config import AudioFeatures
from extraction.extraction_manager import ExtractionManager
from core.logger import get_logger

logger = get_logger("app.services.analysis")


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
        logger.debug("event=analysis.video.start frames=%s", len(frames))
        landmarks = self.extraction.extract_video(frames)
        logger.debug(
            "event=analysis.video.extracted frames=%s landmarks=%s",
            len(frames), len(landmarks) if landmarks else 0,
        )
        return self.analytics.analyze_video(landmarks) if landmarks else None

    def analyze_audio(self, features: AudioFeatures) -> AudioMetrics:
        logger.debug("event=analysis.audio.start samples=%s", features.total_samples)
        metrics = self.analytics.analyze_audio(features)
        logger.debug("event=analysis.audio.done")
        return metrics

    def extract_audio(self, audio: np.ndarray) -> AudioFeatures:
        logger.debug("event=analysis.audio.extract.start samples=%s", audio.size)
        features = self.extraction.extract_audio(audio)
        logger.debug(
            "event=analysis.audio.extract.done samples=%s rms_frames=%s pitch_frames=%s",
            features.total_samples, features.rms.size, features.pitch.size,
        )
        return features

    def transcribe(self, audio: np.ndarray) -> str | None:
        logger.debug("event=analysis.transcribe.start samples=%s", audio.size)
        text = self.extraction.transcribe(audio)
        logger.debug("event=analysis.transcribe.done has_transcript=%s", bool(text))
        return text

    def generate_scores(
        self,
        video: VideoMetrics | None = None,
        audio: AudioMetrics | None = None,
    ) -> Scores | None:
        scores = self.score_calculator.calculate(video, audio)
        logger.debug(
            "event=analysis.scores.done video=%s audio=%s overall=%s",
            video is not None, audio is not None, scores.overall if scores is not None else None,
        )
        return scores
