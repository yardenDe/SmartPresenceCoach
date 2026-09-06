from typing import Any

<<<<<<< Updated upstream
from analytics.metrics.composure_analyzer import ComposureAnalyzer
from analytics.metrics.engagement_analyzer import EngagementAnalyzer
from analytics.metrics.focus_analyzer import FocusAnalyzer
from analytics.metrics.posture_analyzer import PostureAnalyzer
from analytics.metrics.presence_analyzer import PresenceAnalyzer
from analytics.math_utils import average
from core.exceptions import AnalyticsProcessingError
from core.logger import get_logger

logger = get_logger("app.analytics.manager")
=======
from analytics.audio.manager import AudioAnalyticsManager
from analytics.visual.manager import VisualAnalyticsManager
from schemas.analysis import Analysis, AudioFeatures
>>>>>>> Stashed changes


class AnalyticsManager:
    def __init__(self):
        self.analyzers = {
            "focus": FocusAnalyzer(),
            "posture": PostureAnalyzer(),
            "engagement": EngagementAnalyzer(),
            "presence": PresenceAnalyzer(),
            "composure": ComposureAnalyzer(),
        }

<<<<<<< Updated upstream
    def run_full_analysis(self, landmarks: list[dict[str, Any]]) -> dict[str, float]:
        logger.debug("event=analytics.run.start frames=%s", len(landmarks))

        if not landmarks:
            logger.warning("event=analytics.run.empty")
            raise AnalyticsProcessingError()

        try:
            results = {
                analyzer_name: score
                for analyzer_name, analyzer in self.analyzers.items()
                if (score := analyzer.analyze(landmarks)) is not None
            }
        except Exception:
            logger.exception("event=analytics.run.failed")
            raise AnalyticsProcessingError()

        if not results:
            logger.warning("event=analytics.run.no_available_metrics")
            raise AnalyticsProcessingError()

        results["overall"] = average(list(results.values()))
        logger.debug("event=analytics.run.done frames=%s overall=%.2f", len(landmarks), results["overall"])

        return results
=======
    def analyze(
        self,
        landmarks: list[dict[str, Any]] | None = None,
        audio_features: AudioFeatures | None = None,
    ) -> Analysis:
        return Analysis(
            visual=(
                self.visual.run_full_analysis(landmarks)
                if landmarks is not None
                else None
            ),
            audio=(
                self.audio.analyze(audio_features)
                if audio_features is not None
                else None
            ),
        )
>>>>>>> Stashed changes
