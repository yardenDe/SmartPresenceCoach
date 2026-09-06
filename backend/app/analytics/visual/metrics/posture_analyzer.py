from typing import Any

from analytics.visual.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_score,
    axis_distance,
    line_angle_degrees,
    midpoint,
    percentage_of,
    point_variance,
    subtract_from,
    weighted_average,
)


class PostureAnalyzer(BaseAnalyzer):
    HEAD_STABILITY_WEIGHT = 0.2
    SHOULDER_TILT_WEIGHT = 0.25
    BODY_TILT_WEIGHT = 0.25
    HEAD_TILT_SCORE_WEIGHT = 0.3
    HORIZONTAL_ANGLE = 180.0
    MAX_HEAD_POSITION_VARIANCE = 0.2
    MAX_SHOULDER_TILT = 0.25
    MAX_BODY_TILT = 0.33
    MAX_HEAD_TILT_DEGREES = 25.0

    def _analyze_head_stability(self, frames: list[dict[str, Any]]) -> float | None:
        nose_positions = self._collect_points(frames, "pose", "nose")

        if len(nose_positions) <= 1:
            return None

        head_position_variance = point_variance(nose_positions)
        variance_percentage = percentage_of(head_position_variance, self.MAX_HEAD_POSITION_VARIANCE)

        return subtract_from(variance_percentage)

    def _score_shoulder_tilt(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not self._has_points(pose_data, "left_shoulder", "right_shoulder"):
            return None

        shoulder_tilt = axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "y",
        )
        tilt_percentage = percentage_of(shoulder_tilt, self.MAX_SHOULDER_TILT)

        return subtract_from(tilt_percentage)

    def _score_body_tilt(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not self._has_points(
            pose_data,
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
        ):
            return None

        shoulder_center = midpoint(pose_data["left_shoulder"], pose_data["right_shoulder"])
        hip_center = midpoint(pose_data["left_hip"], pose_data["right_hip"])
        body_tilt = axis_distance(shoulder_center, hip_center, "x")
        tilt_percentage = percentage_of(body_tilt, self.MAX_BODY_TILT)

        return subtract_from(tilt_percentage)

    def _score_head_tilt(self, frame_data: dict[str, Any]) -> float | None:
        face_data = frame_data.get("face")

        if self._has_points(face_data, "left_cheek", "right_cheek"):
            angle = line_angle_degrees(face_data["left_cheek"], face_data["right_cheek"])
        elif self._has_points(face_data, "left_eye_outer", "right_eye_outer"):
            angle = line_angle_degrees(face_data["left_eye_outer"], face_data["right_eye_outer"])
        else:
            return None

        head_tilt = min(angle, abs(self.HORIZONTAL_ANGLE - angle))
        tilt_percentage = percentage_of(head_tilt, self.MAX_HEAD_TILT_DEGREES)

        return subtract_from(tilt_percentage)

    def _analyze_shoulder_tilt(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_shoulder_tilt(frame_data)) is not None
        ]

        return average_score(scores)

    def _analyze_body_tilt(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_body_tilt(frame_data)) is not None
        ]

        return average_score(scores)

    def _analyze_head_tilt(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_head_tilt(frame_data)) is not None
        ]

        return average_score(scores)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_stability_score = self._analyze_head_stability(frames)
        shoulder_tilt_score = self._analyze_shoulder_tilt(frames)
        body_tilt_score = self._analyze_body_tilt(frames)
        head_tilt_score = self._analyze_head_tilt(frames)

        return weighted_average([
            (head_stability_score, self.HEAD_STABILITY_WEIGHT) if head_stability_score is not None else None,
            (shoulder_tilt_score, self.SHOULDER_TILT_WEIGHT) if shoulder_tilt_score is not None else None,
            (body_tilt_score, self.BODY_TILT_WEIGHT) if body_tilt_score is not None else None,
            (head_tilt_score, self.HEAD_TILT_SCORE_WEIGHT) if head_tilt_score is not None else None,
        ])
