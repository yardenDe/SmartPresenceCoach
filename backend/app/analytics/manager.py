from typing import Any

from analytics.metrics.composure_analyzer import ComposureAnalyzer
from analytics.metrics.focus_analyzer import FocusAnalyzer
from analytics.metrics.posture_analyzer import PostureAnalyzer
from analytics.metrics.presence_analyzer import PresenceAnalyzer
from analytics.metrics.vitality_analyzer import VitalityAnalyzer
from analytics.math_utils import average


class AnalyticsManager:
    def __init__(self) -> None:
        self.analyzers = {
            "focus": FocusAnalyzer(),
            "posture": PostureAnalyzer(),
            "vitality": VitalityAnalyzer(),
            "presence": PresenceAnalyzer(),
            "composure": ComposureAnalyzer(),
        }

    def run_full_analysis(self, landmarks: list[dict[str, Any]]) -> dict[str, float]:
        results = {
            analyzer_name: analyzer.analyze(landmarks)
            for analyzer_name, analyzer in self.analyzers.items()
        }

        results["overall"] = average(list(results.values()))

        return results