from typing import Any

from analytics.math_utils import average_available, line_angle_degrees
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class ShoulderTiltAnalyzer(BaseAnalyzer):
    HORIZONTAL_ANGLE = 180.0

    def _calculate_tilt(
        self,
        pose_data: dict[str, Any],
    ) -> float | None:
        if not self._has_points(
            pose_data,
            "left_shoulder",
            "right_shoulder",
        ):
            return None

        angle = line_angle_degrees(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
        )

        return min(angle, abs(self.HORIZONTAL_ANGLE - angle))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        tilts = [
            tilt
            for frame_data in frames
            if (pose_data := frame_data.get("pose")) is not None
            and (tilt := self._calculate_tilt(pose_data)) is not None
        ]

        return average_available(tilts)
