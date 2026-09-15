from vision.config import FrameLandmarks

from analytics.visual.metrics.face_direction_analyzer import FaceDirectionAnalyzer
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
            "face_direction": FaceDirectionAnalyzer(),
            "movement_amount": MovementAmountAnalyzer(),
            "movement_variation": MovementVariationAnalyzer(),
            "head_movement": HeadMovementAnalyzer(),
            "shoulder_tilt": ShoulderTiltAnalyzer(),
            "hand_movement": HandMovementAnalyzer(),
        }

    def analyze(self, landmarks: list[FrameLandmarks]) -> VisualMetrics:
        logger.debug("event=analytics.run.start frames=%s", len(landmarks))

        if not landmarks:
            logger.warning("event=analytics.run.empty")
            raise AnalyticsProcessingError()

        try:
            results = {}

            for analyzer_name, analyzer in self.analyzers.items():
                score = analyzer.analyze(landmarks)

                if score is not None:
                    results[analyzer_name] = score
        except Exception:
            logger.exception("event=analytics.run.failed")
            raise AnalyticsProcessingError()

        if not results:
            logger.warning("event=analytics.run.no_available_metrics")
            raise AnalyticsProcessingError()

        logger.debug("event=analytics.run.done frames=%s", len(landmarks))

        return VisualMetrics(**results)
