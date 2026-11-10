from extraction.video.config import FrameLandmarks

from analytics.visual.config import BODY_POINTS
from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class MovementAmountAnalyzer(BaseAnalyzer):

    def analyze(self, frames: list[FrameLandmarks]) -> float | None:
        motions = self._normalized_motion_series(
            frames,
            BODY_POINTS,
        )

        return average_available(motions)
