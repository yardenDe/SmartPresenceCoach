from analytics.audio.audio_analytics_manager import AudioAnalyticsManager
from analytics.config import AudioMetrics, VideoMetrics
from analytics.visual.visual_analytics_manager import VisualAnalyticsManager
from extraction.audio.config import AudioFeatures
from extraction.video.config import FrameLandmarks


class AnalyticsManager:
    def __init__(
        self,
        visual: VisualAnalyticsManager,
        audio: AudioAnalyticsManager,
    ):
        self.visual = visual
        self.audio = audio

    def analyze_video(self, landmarks: list[FrameLandmarks]) -> VideoMetrics:
        return self.visual.analyze(landmarks)

    def analyze_audio(self, features: AudioFeatures) -> AudioMetrics:
        return self.audio.analyze(features)
