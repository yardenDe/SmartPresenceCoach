
import numpy as np

from analytics.manager import AnalyticsManager
from analytics.score_calculator import ScoreCalculator
from audio.audio_pipeline import AudioPipeline
from models.analysis_data import AudioMetric, Transcript, VideoMetric
from schemas.analysis import Scores
from vision.vision_pipeline import VisionPipeline


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

    def analyze_video(
        self,
        session_id: int,
        start_time: float,
        end_time: float,
        frames: list[np.ndarray],
    ) -> VideoMetric | None:
        landmarks = self.vision_pipeline.process(frames) or None
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
        if self.audio_pipeline is None:
            return None

        features = self.audio_pipeline.extract_features(audio)
        metrics = self.analytics.analyze(audio_features=features).audio

        if metrics is None:
            return None

        return AudioMetric(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            **metrics.model_dump(exclude={"transcript"}),
        )

    @property
    def transcription_enabled(self) -> bool:
        return (
            self.audio_pipeline is not None
            and self.audio_pipeline.transcriber is not None
        )

    def transcribe(
        self,
        session_id: int,
        start_time: float,
        end_time: float,
        audio: np.ndarray,
    ) -> Transcript | None:
        if self.audio_pipeline is None:
            return None

        text = self.audio_pipeline.transcribe(audio)

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
        video: VideoMetric,
        audio: AudioMetric | None = None,
    ) -> Scores | None:
        return self.score_calculator.calculate(video, audio)
