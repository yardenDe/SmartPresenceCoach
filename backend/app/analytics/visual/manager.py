from typing import Any

from analytics.visual.metrics.composure_analyzer import ComposureAnalyzer
from analytics.visual.metrics.engagement_analyzer import EngagementAnalyzer
from analytics.visual.metrics.focus_analyzer import FocusAnalyzer
from analytics.visual.metrics.posture_analyzer import PostureAnalyzer
from analytics.visual.metrics.presence_analyzer import PresenceAnalyzer
from analytics.math_utils import average
from core.exceptions import AnalyticsProcessingError
from core.logger import get_logger
from schemas.analysis import VisualAnalysis

logger = get_logger("app.analytics.visual.manager")


class VisualAnalyticsManager:
    def __init__(self):
        self.analyzers = {
            "focus": FocusAnalyzer(),
            "posture": PostureAnalyzer(),
            "engagement": EngagementAnalyzer(),
            "presence": PresenceAnalyzer(),
            "composure": ComposureAnalyzer(),
        }

    def run_full_analysis(self, landmarks: list[dict[str, Any]]) -> VisualAnalysis:
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

        return VisualAnalysis(**results)
