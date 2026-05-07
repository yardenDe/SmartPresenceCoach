from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    axis_distance,
    clamp_score,
    midpoint_axis_distance,
    normalize_inverse,
    points_exist,
    weighted_average,
)


class PostureAnalyzer(BaseAnalyzer):
    SHOULDER_ALIGNMENT_WEIGHT = 0.65
    UPPER_BODY_TILT_WEIGHT = 0.35
    SHOULDER_ALIGNMENT_SCALE = 400.0
    UPPER_BODY_TILT_SCALE = 300.0
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE

    def _score_shoulder_alignment(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not points_exist(pose_data, "left_shoulder", "right_shoulder"):
            return None

        shoulder_gap = axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "y",
        )

        return normalize_inverse(shoulder_gap, self.SHOULDER_ALIGNMENT_SCALE, self.DEFAULT_SCORE)

    def _score_upper_body_tilt(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not points_exist(
            pose_data,
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
        ):
            return None

        tilt = midpoint_axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            pose_data["left_hip"],
            pose_data["right_hip"],
            "x",
        )
        return normalize_inverse(tilt, self.UPPER_BODY_TILT_SCALE, self.DEFAULT_SCORE)

    def _analyze_shoulder_alignment(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_shoulder_alignment(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def _analyze_upper_body_tilt(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_upper_body_tilt(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        shoulder_score = self._analyze_shoulder_alignment(frames)
        upper_body_tilt_score = self._analyze_upper_body_tilt(frames)

        return weighted_average([
            (shoulder_score, self.SHOULDER_ALIGNMENT_WEIGHT) if shoulder_score is not None else None,
            (
                upper_body_tilt_score,
                self.UPPER_BODY_TILT_WEIGHT,
            ) if upper_body_tilt_score is not None else None,
        ])
