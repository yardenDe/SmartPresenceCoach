from typing import Any

from schemas.analysis import AudioAnalysis


class AudioAnalyticsManager:
    def run_full_analysis(
        self,
        audio_features: Any,
    ) -> AudioAnalysis:
        raise NotImplementedError
