from analytics.composure_analyzer import ComposureAnalyzer
from analytics.focus_analyzer import FocusAnalyzer
from analytics.posture_analyzer import PostureAnalyzer
from analytics.presence_analyzer import PresenceAnalyzer
from analytics.vitality_analyzer import VitalityAnalyzer


class AnalyticsManager:
    def __init__(self):
        self.analyzers = {
            "focus": FocusAnalyzer(),
            "posture": PostureAnalyzer(),
            "vitality": VitalityAnalyzer(),
            "presence": PresenceAnalyzer(),
            "composure": ComposureAnalyzer(),
        }

    def run_full_analysis(self, landmarks):
        return {
            analyzer_name: analyzer.analyze(landmarks)
            for analyzer_name, analyzer in self.analyzers.items()
        }
