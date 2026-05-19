from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_score,
    axis_distance,
    midpoint,
    normalize_inverse,
    point_distance,
    weighted_average,
)


class FocusAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.2
    BODY_WEIGHT = 0.3
    ADVANCED_WEIGHT = 0.5
    SCREEN_CENTER_X = 0.5
    SCREEN_CENTER_SCALE = 200.0
    BODY_ALIGNMENT_SCALE = 250.0
    EYE_DEVIATION_SCALE = 500.0
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE

    def _score_screen_center(self, pose_data: dict[str, Any] | None) -> float | None:
        if not self._has_point(pose_data, "nose"):
            return None

        nose = pose_data["nose"]
        deviation = abs(nose["x"] - self.SCREEN_CENTER_X)

        return normalize_inverse(deviation, self.SCREEN_CENTER_SCALE, self.DEFAULT_SCORE)

    def _score_body_alignment(self, pose_data: dict[str, Any] | None) -> float | None:
        if not self._has_points(pose_data, "nose", "left_shoulder", "right_shoulder"):
            return None

        shoulder_center = midpoint(pose_data["left_shoulder"], pose_data["right_shoulder"])
        head_deviation = axis_distance(pose_data["nose"], shoulder_center, "x")

        return normalize_inverse(head_deviation, self.BODY_ALIGNMENT_SCALE, self.DEFAULT_SCORE)

    def _score_eye_alignment(self, face_data: dict[str, Any] | None) -> float | None:
        left_eye_ready = self._has_points(face_data, "left_iris_center", "left_eye_outer", "left_eye_inner")
        right_eye_ready = self._has_points(face_data, "right_iris_center", "right_eye_inner", "right_eye_outer")

        if not left_eye_ready and not right_eye_ready:
            return None

        scores = []

        left_eye_center = midpoint(face_data["left_eye_outer"], face_data["left_eye_inner"])
        left_deviation = point_distance(face_data["left_iris_center"], left_eye_center)
        scores.append(normalize_inverse(left_deviation, self.EYE_DEVIATION_SCALE, self.DEFAULT_SCORE))

        right_eye_center = midpoint(face_data["right_eye_inner"], face_data["right_eye_outer"])
        right_deviation = point_distance(face_data["right_iris_center"], right_eye_center)
        scores.append(normalize_inverse(right_deviation, self.EYE_DEVIATION_SCALE, self.DEFAULT_SCORE))

        return average_score(scores)

    def _analyze_screen_center(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_screen_center(frame_data.get("pose"))) is not None
        ]

        return average_score(scores)

    def _analyze_body_alignment(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_body_alignment(frame_data.get("pose"))) is not None
        ]

        return average_score(scores)

    def _analyze_eye_alignment(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_eye_alignment(frame_data.get("face"))) is not None
        ]

        return average_score(scores)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        screen_score = self._analyze_screen_center(frames)
        body_score = self._analyze_body_alignment(frames)
        eye_score = self._analyze_eye_alignment(frames)

        return weighted_average([
            (screen_score, self.BASIC_WEIGHT) if screen_score is not None else None,
            (body_score, self.BODY_WEIGHT) if body_score is not None else None,
            (eye_score, self.ADVANCED_WEIGHT) if eye_score is not None else None,
        ])
