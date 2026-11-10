
import numpy as np

from analytics.manager import AnalyticsManager
from analytics.score_calculator import ScoreCalculator
from extraction.manager import ExtractionManager
from models.analysis import AudioMetric, Transcript, VideoMetric
from schemas.analysis import Scores


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

    def analyze_video(
        self,
        session_id: int,
        start_time: float,
        end_time: float,
        frames: list[np.ndarray],
    ) -> VideoMetric | None:
        landmarks = self.extraction.extract_video(frames) or None
        metrics = self.analytics.analyze(landmarks=landmarks).visual

        if metrics is None:
            return None

        return VideoMetric(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            **metrics.model_dump(),
        )

    def analyze_audio(
        self,
        session_id: int,
        start_time: float,
        end_time: float,
        audio: np.ndarray,
    ) -> AudioMetric | None:
        features = self.extraction.extract_audio(audio)
        metrics = self.analytics.analyze(audio_features=features).audio

        if metrics is None:
            return None

        return AudioMetric(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            **metrics.model_dump(),
        )

    def transcribe(
        self,
        session_id: int,
        start_time: float,
        end_time: float,
        audio: np.ndarray,
    ) -> Transcript | None:
        text = self.extraction.transcribe(audio)

        if text is None:
            return None

        return Transcript(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            transcript=text,
        )

    def generate_scores(
        self,
        video: VideoMetric | None = None,
        audio: AudioMetric | None = None,
    ) -> Scores | None:
        return self.score_calculator.calculate(video, audio)