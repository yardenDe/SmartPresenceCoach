from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, axis_distance, clamp_score, points_exist


class PresenceAnalyzer(BaseAnalyzer):
    ELBOW_DISTANCE_SCALE = 200.0

    def _compute_frame_score(self, frame_data: dict[str, Any]) -> float:
        pose_data = frame_data.get("pose")

        if not points_exist(pose_data, "left_elbow", "right_elbow"):
            return 0.0

        elbow_distance = axis_distance(
            pose_data["left_elbow"],
            pose_data["right_elbow"],
            "x",
        )

        return clamp_score(elbow_distance * self.ELBOW_DISTANCE_SCALE)

    def compute(self, window_data: list[dict[str, Any]]) -> float:
        frame_scores = [self._compute_frame_score(frame_data) for frame_data in window_data]
        return clamp_score(average(frame_scores))

    def analyze(self, data: dict[str, Any] | list[dict[str, Any]]) -> float:
        if isinstance(data, list):
            return self.compute(data)
        return self.compute([data])
