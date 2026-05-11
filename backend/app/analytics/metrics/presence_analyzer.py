from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, axis_distance, clamp_score, normalize_direct, points_exist, weighted_average


class PresenceAnalyzer(BaseAnalyzer):
    ELBOW_DISTANCE_WEIGHT = 1.0
    ELBOW_DISTANCE_SCALE = 200.0

    def _score_elbow_distance(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not points_exist(pose_data, "left_elbow", "right_elbow"):
            return None

        elbow_distance = axis_distance(
            pose_data["left_elbow"],
            pose_data["right_elbow"],
            "x",
        )

        return normalize_direct(elbow_distance, self.ELBOW_DISTANCE_SCALE)

    def _analyze_elbow_distance(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_elbow_distance(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        elbow_score = self._analyze_elbow_distance(frames)

        return weighted_average([
            (elbow_score, self.ELBOW_DISTANCE_WEIGHT) if elbow_score is not None else None
        ])
