from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    axis_distance,
    clamp_score,
    midpoint,
    point_distance,
    point_exists,
    points_exist,
    ratio,
    weighted_average,
)


class FocusAnalyzer(BaseAnalyzer):
    HEAD_DEVIATION_SCALE = 150.0
    EYE_DEVIATION_SCALE = 500.0
    HEAD_WEIGHT = 0.3
    EYE_WEIGHT = 0.7
    DEFAULT_SCORE = 100.0

    def _compute_head_score(self, pose_data: dict[str, Any] | None) -> float | None:
        if not point_exists(pose_data, "nose"):
            return None

        nose = pose_data["nose"]
        left_eye = pose_data.get("left_eye_basic")
        right_eye = pose_data.get("right_eye_basic")

        if left_eye and right_eye:
            left_distance = axis_distance(nose, left_eye, "x")
            right_distance = axis_distance(nose, right_eye, "x")

            if left_distance + right_distance == 0:
                return self.DEFAULT_SCORE

            head_ratio = ratio(left_distance, right_distance)
            head_deviation = abs(1 - head_ratio)
        else:
            head_deviation = abs(nose["x"] - 0.5)

        return clamp_score(self.DEFAULT_SCORE - (head_deviation * self.HEAD_DEVIATION_SCALE))

    def _compute_eye_score(self, face_data: dict[str, Any] | None) -> float | None:
        if not points_exist(face_data, "iris_center", "left_eyebrow", "right_eyebrow"):
            return None

        iris_center = face_data["iris_center"]
        eye_left_corner = face_data["left_eyebrow"]
        eye_right_corner = face_data["right_eyebrow"]

        eye_center = midpoint(eye_left_corner, eye_right_corner)
        eye_deviation = point_distance(iris_center, eye_center)

        return clamp_score(self.DEFAULT_SCORE - (eye_deviation * self.EYE_DEVIATION_SCALE))

    def _compute_frame_score(self, frame_data: dict[str, Any]) -> float | None:
        head_score = self._compute_head_score(frame_data.get("pose"))
        eye_score = self._compute_eye_score(frame_data.get("face"))

        if eye_score is None:
            return head_score

        if head_score is None:
            return eye_score

        return clamp_score(
            weighted_average([
                (eye_score, self.EYE_WEIGHT),
                (head_score, self.HEAD_WEIGHT),
            ])
        )

    def compute(self, window_data: list[dict[str, Any]]) -> float:
        frame_scores = [
            score
            for frame_data in window_data
            if (score := self._compute_frame_score(frame_data)) is not None
        ]
        return clamp_score(average(frame_scores))

    def analyze(self, data: dict[str, Any] | list[dict[str, Any]]) -> float:
        if isinstance(data, list):
            return self.compute(data)
        return self.compute([data])
