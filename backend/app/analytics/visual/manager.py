from typing import Any

from analytics.visual.metrics.gaze_direction_analyzer import GazeDirectionAnalyzer
from analytics.visual.metrics.hand_movement_analyzer import HandMovementAnalyzer
from analytics.visual.metrics.head_movement_analyzer import HeadMovementAnalyzer
from analytics.visual.metrics.movement_amount_analyzer import MovementAmountAnalyzer
from analytics.visual.metrics.movement_variation_analyzer import MovementVariationAnalyzer
from analytics.visual.metrics.shoulder_tilt_analyzer import ShoulderTiltAnalyzer
from core.exceptions import AnalyticsProcessingError
from core.logger import get_logger
from schemas.analysis import VisualMetrics

logger = get_logger("app.analytics.visual.manager")


class VisualAnalyticsManager:
    def __init__(self):
        self.analyzers = {
            "gaze_direction": GazeDirectionAnalyzer(),
            "movement_amount": MovementAmountAnalyzer(),
            "movement_variation": MovementVariationAnalyzer(),
            "head_movement": HeadMovementAnalyzer(),
            "shoulder_tilt": ShoulderTiltAnalyzer(),
            "hand_movement": HandMovementAnalyzer(),
        }

    def analyze(self, landmarks: list[dict[str, Any]]) -> VisualMetrics:
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

        logger.debug("event=analytics.run.done frames=%s", len(landmarks))

        return VisualMetrics(**results)
