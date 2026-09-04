from typing import Any

from analytics.visual.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_score,
    axis_distance,
    midpoint,
    percentage_of,
    point_distance,
    subtract_from,
    weighted_average,
)


class FocusAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.2
    BODY_WEIGHT = 0.3
    ADVANCED_WEIGHT = 0.5
    SCREEN_CENTER_X = 0.5
    MAX_SCREEN_DEVIATION = 0.15
    MAX_BODY_DEVIATION = 0.12
    MAX_EYE_DEVIATION = 0.02

    def _score_screen_center(self, pose_data: dict[str, Any] | None) -> float | None:
        if not self._has_point(pose_data, "nose"):
            return None

        nose = pose_data["nose"]
        deviation = abs(nose["x"] - self.SCREEN_CENTER_X)
        deviation_percentage = percentage_of(deviation, self.MAX_SCREEN_DEVIATION)

        return subtract_from(deviation_percentage)

    def _score_body_alignment(self, pose_data: dict[str, Any] | None) -> float | None:
        if not self._has_points(pose_data, "nose", "left_shoulder", "right_shoulder"):
            return None

        shoulder_center = midpoint(pose_data["left_shoulder"], pose_data["right_shoulder"])
        head_deviation = axis_distance(pose_data["nose"], shoulder_center, "x")
        deviation_percentage = percentage_of(head_deviation, self.MAX_BODY_DEVIATION)

        return subtract_from(deviation_percentage)

    def _score_eye_alignment(self, face_data: dict[str, Any] | None) -> float | None:
        left_eye_ready = self._has_points(face_data, "left_iris_center", "left_eye_outer", "left_eye_inner")
        right_eye_ready = self._has_points(face_data, "right_iris_center", "right_eye_inner", "right_eye_outer")

        if not left_eye_ready and not right_eye_ready:
            return None

        scores = []

        if left_eye_ready:
            left_eye_center = midpoint(face_data["left_eye_outer"], face_data["left_eye_inner"])
            left_deviation = point_distance(face_data["left_iris_center"], left_eye_center)
            left_deviation_percentage = percentage_of(left_deviation, self.MAX_EYE_DEVIATION)
            scores.append(subtract_from(left_deviation_percentage))

        if right_eye_ready:
            right_eye_center = midpoint(face_data["right_eye_inner"], face_data["right_eye_outer"])
            right_deviation = point_distance(face_data["right_iris_center"], right_eye_center)
            right_deviation_percentage = percentage_of(right_deviation, self.MAX_EYE_DEVIATION)
            scores.append(subtract_from(right_deviation_percentage))

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
