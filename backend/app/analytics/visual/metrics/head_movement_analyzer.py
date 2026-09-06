from math import atan2, degrees
from typing import Any

from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer
from media.config import TARGET_FPS


class HeadMovementAnalyzer(BaseAnalyzer):
    def _calculate_direction(
        self,
        pose_data: dict[str, Any],
    ) -> float | None:
        if not self._has_point(pose_data, "nose"):
            return None

        face_center = self._face_center(pose_data)
        face_width = self._face_width(pose_data)

        if face_center is None or face_width is None or face_width <= 0:
            return None

        horizontal_offset = (
            pose_data["nose"]["x"] - face_center["x"]
        )

        return degrees(atan2(horizontal_offset, face_width))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        directions = [
            direction
            for frame_data in frames
            if (pose_data := frame_data.get("pose")) is not None
            and (direction := self._calculate_direction(pose_data)) is not None
        ]

        if len(directions) < 2:
            return None

        changes = [
            abs(directions[index] - directions[index - 1]) * TARGET_FPS
            for index in range(1, len(directions))
        ]

        return average_available(changes)
