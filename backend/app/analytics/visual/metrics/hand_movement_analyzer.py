from typing import Any

from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class HandMovementAnalyzer(BaseAnalyzer):
    ARM_POINTS = [
        "left_elbow",
        "right_elbow",
        "left_wrist_basic",
        "right_wrist_basic",
    ]

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        motions = self._normalized_motion_series(
            frames,
            self.ARM_POINTS,
        )

        return average_available(motions)
