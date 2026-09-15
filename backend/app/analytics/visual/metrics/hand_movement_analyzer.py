from vision.config import FrameLandmarks

from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class HandMovementAnalyzer(BaseAnalyzer):
    ARM_POINTS = [
        "left_elbow",
        "right_elbow",
        "left_wrist",
        "right_wrist",
    ]

    def analyze(self, frames: list[FrameLandmarks]) -> float | None:
        motions = self._normalized_motion_series(
            frames,
            self.ARM_POINTS,
        )

        return average_available(motions)
