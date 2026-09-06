from statistics import pstdev
from typing import Any

from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class MovementVariationAnalyzer(BaseAnalyzer):
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

        if not motions:
            return None

        if len(motions) == 1:
            return 0.0

        return float(pstdev(motions))
