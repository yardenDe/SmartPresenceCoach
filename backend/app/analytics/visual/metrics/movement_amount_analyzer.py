from typing import Any

from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class MovementAmountAnalyzer(BaseAnalyzer):
    BODY_POINTS = [
        "nose",
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist_basic",
        "right_wrist_basic",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
    ]

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        motions = self._normalized_motion_series(
            frames,
            self.BODY_POINTS,
        )

        return average_available(motions)
