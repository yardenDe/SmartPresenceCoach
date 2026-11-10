from statistics import pstdev
from extraction.video.config import FrameLandmarks
from analytics.visual.config import BODY_POINTS

from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class MovementVariationAnalyzer(BaseAnalyzer):

    def analyze(self, frames: list[FrameLandmarks]) -> float | None:
        motions = self._normalized_motion_series(
            frames,
            BODY_POINTS,
        )

        if not motions:
            return None

        if len(motions) == 1:
            return 0.0

        return float(pstdev(motions))
