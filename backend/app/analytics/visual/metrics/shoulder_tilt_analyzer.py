from typing import Any

from analytics.math_utils import average_available, line_angle_degrees
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class ShoulderTiltAnalyzer(BaseAnalyzer):
    HORIZONTAL_ANGLE = 180.0

    def _calculate_tilt(
        self,
        landmarks: dict[str, Any],
    ) -> float | None:
        if not self._has_points(
            landmarks,
            "left_shoulder",
            "right_shoulder",
        ):
            return None

        angle = line_angle_degrees(
            landmarks["left_shoulder"],
            landmarks["right_shoulder"],
        )

        return min(angle, abs(self.HORIZONTAL_ANGLE - angle))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        tilts = [
            tilt
            for landmarks in frames
            if (tilt := self._calculate_tilt(landmarks)) is not None
        ]

        return average_available(tilts)
