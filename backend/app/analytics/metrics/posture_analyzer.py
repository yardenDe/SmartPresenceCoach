from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_score,
    axis_distance,
    clamp_score,
    line_angle_degrees,
    midpoint,
    normalize_inverse,
    second_half_average_increase,
    variance,
    weighted_average,
)


class PostureAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.2
    BODY_WEIGHT = 0.5
    ADVANCED_WEIGHT = 0.3
    SHOULDER_ALIGNMENT_WEIGHT = 0.5
    UPPER_BODY_TILT_WEIGHT = 0.5
    HEAD_DROP_WEIGHT = 0.7
    HEAD_DROP_STABILITY_WEIGHT = 0.3
    HORIZONTAL_ANGLE = 180.0
    HEAD_DROP_SCALE = 300.0
    HEAD_DROP_VARIANCE_SCALE = 500.0
    SHOULDER_ALIGNMENT_SCALE = 400.0
    UPPER_BODY_TILT_SCALE = 300.0
    HEAD_TILT_SCALE = 4.0
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE

    def _analyze_head_drop(self, frames: list[dict[str, Any]]) -> float | None:
        nose_positions_y = self._collect_axis_values(frames, "pose", "nose", "y")

        if len(nose_positions_y) < 2:
            return None

        drop_score = normalize_inverse(
            second_half_average_increase(nose_positions_y),
            self.HEAD_DROP_SCALE,
            self.DEFAULT_SCORE,
        )
        stability_score = normalize_inverse(
            variance(nose_positions_y),
            self.HEAD_DROP_VARIANCE_SCALE,
            self.DEFAULT_SCORE,
        )

        return clamp_score(weighted_average([
            (drop_score, self.HEAD_DROP_WEIGHT),
            (stability_score, self.HEAD_DROP_STABILITY_WEIGHT),
        ]) or 0.0)

    def _score_shoulder_alignment(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not self._has_points(pose_data, "left_shoulder", "right_shoulder"):
            return None

        shoulder_gap = axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "y",
        )

        return normalize_inverse(shoulder_gap, self.SHOULDER_ALIGNMENT_SCALE, self.DEFAULT_SCORE)

    def _score_upper_body_tilt(self, frame_data: dict[str, Any]) -> float | None:
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
        tilt = axis_distance(shoulder_center, hip_center, "x")
        return normalize_inverse(tilt, self.UPPER_BODY_TILT_SCALE, self.DEFAULT_SCORE)

    def _score_head_tilt(self, frame_data: dict[str, Any]) -> float | None:
        face_data = frame_data.get("face")

        if self._has_points(face_data, "left_cheek", "right_cheek"):
            angle = line_angle_degrees(face_data["left_cheek"], face_data["right_cheek"])
        elif self._has_points(face_data, "left_eye_outer", "right_eye_outer"):
            angle = line_angle_degrees(face_data["left_eye_outer"], face_data["right_eye_outer"])
        else:
            return None

        head_tilt = min(angle, abs(self.HORIZONTAL_ANGLE - angle))
        return normalize_inverse(head_tilt, self.HEAD_TILT_SCALE, self.DEFAULT_SCORE)

    def _score_body_posture(self, frame_data: dict[str, Any]) -> float | None:
        shoulder_score = self._score_shoulder_alignment(frame_data)
        tilt_score = self._score_upper_body_tilt(frame_data)

        return weighted_average([
            (shoulder_score, self.SHOULDER_ALIGNMENT_WEIGHT) if shoulder_score is not None else None,
            (tilt_score, self.UPPER_BODY_TILT_WEIGHT) if tilt_score is not None else None,
        ])

    def _analyze_body_posture(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_body_posture(frame_data)) is not None
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
        head_drop_score = self._analyze_head_drop(frames)
        body_score = self._analyze_body_posture(frames)
        head_tilt_score = self._analyze_head_tilt(frames)

        return weighted_average([
            (head_drop_score, self.BASIC_WEIGHT) if head_drop_score is not None else None,
            (body_score, self.BODY_WEIGHT) if body_score is not None else None,
            (head_tilt_score, self.ADVANCED_WEIGHT) if head_tilt_score is not None else None,
        ])
