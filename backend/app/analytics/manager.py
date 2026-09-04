from typing import Any

from analytics.audio.manager import AudioAnalyticsManager
from analytics.visual.manager import VisualAnalyticsManager
from schemas.analysis import AudioAnalysis, VisualAnalysis


class AnalyticsManager:
    def __init__(
        self,
        visual: VisualAnalyticsManager,
        audio: AudioAnalyticsManager,
    ):
        self.visual = visual
        self.audio = audio

    def analyze_visual(
        self,
        landmarks: list[dict[str, Any]],
    ) -> VisualAnalysis:
        return self.visual.run_full_analysis(landmarks)

    def analyze_audio(
        self,
        audio_features: Any,
    ) -> AudioAnalysis:
        return self.audio.run_full_analysis(audio_features)
