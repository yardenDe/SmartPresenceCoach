from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    axis_distance,
    clamp_score,
    difference,
    midpoint,
    normalize_inverse,
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
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE

    def _score_head_alignment(self, pose_data: dict[str, Any] | None) -> float | None:
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
            head_deviation = difference(1, head_ratio)
        else:
            head_deviation = difference(nose["x"], 0.5)

        return normalize_inverse(head_deviation, self.HEAD_DEVIATION_SCALE, self.DEFAULT_SCORE)

    def _score_eye_alignment(self, face_data: dict[str, Any] | None) -> float | None:
        if not points_exist(face_data, "iris_center", "left_eyebrow", "right_eyebrow"):
            return None

        iris_center = face_data["iris_center"]
        eye_left_corner = face_data["left_eyebrow"]
        eye_right_corner = face_data["right_eyebrow"]

        eye_center = midpoint(eye_left_corner, eye_right_corner)
        eye_deviation = point_distance(iris_center, eye_center)

        return normalize_inverse(eye_deviation, self.EYE_DEVIATION_SCALE, self.DEFAULT_SCORE)

    def _analyze_head_alignment(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_head_alignment(frame_data.get("pose"))) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def _analyze_eye_alignment(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_eye_alignment(frame_data.get("face"))) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_score = self._analyze_head_alignment(frames)
        eye_score = self._analyze_eye_alignment(frames)

        return weighted_average([
            (head_score, self.HEAD_WEIGHT) if head_score is not None else None,
            (eye_score, self.EYE_WEIGHT) if eye_score is not None else None,
        ])
