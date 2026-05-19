from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_available,
    normalize_inverse,
    point_in_bounds,
    point_variance,
    weighted_average,
)


class ComposureAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.4
    BODY_WEIGHT = 0.3
    ADVANCED_WEIGHT = 0.3
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE
    TOUCH_PENALTY_SCALE = 100.0
    TOUCH_DETECTED = 1.0
    TOUCH_CLEAR = 0.0
    HEAD_MOVEMENT_VARIANCE_SCALE = 500.0
    SHOULDER_FIDGET_SCALE = 900.0
    SHOULDER_POINTS = ["left_shoulder", "right_shoulder"]
    FACE_TOP_POINT = "forehead"
    FACE_BOTTOM_POINT = "chin"
    FACE_LEFT_POINT = "left_cheek"
    FACE_RIGHT_POINT = "right_cheek"
    FINGERTIP_POINTS = [
        "hand_thumb_tip",
        "hand_index_tip",
        "hand_middle_tip",
        "hand_ring_tip",
        "hand_pinky_tip",
    ]

    def _analyze_head_stability(self, frames: list[dict[str, Any]]) -> float | None:
        nose_positions = self._collect_points(frames, "pose", "nose")

        if not nose_positions:
            return None

        if len(nose_positions) == 1:
            return self.DEFAULT_SCORE

        return normalize_inverse(
            point_variance(nose_positions),
            self.HEAD_MOVEMENT_VARIANCE_SCALE,
            self.DEFAULT_SCORE,
        )

    def _analyze_shoulder_fidgeting(self, frames: list[dict[str, Any]]) -> float | None:
        shoulder_motion = self._average_named_point_motion(frames, "pose", self.SHOULDER_POINTS)
        if shoulder_motion is None:
            return None

        return normalize_inverse(shoulder_motion, self.SHOULDER_FIDGET_SCALE, self.DEFAULT_SCORE)

    def _score_face_touch(self, frame_data: dict[str, Any]) -> float | None:
        face_data = frame_data.get("face")
        hands = frame_data.get("hands", [])

        if not face_data or not hands:
            return None

        if not self._has_points(
            face_data,
            self.FACE_TOP_POINT,
            self.FACE_BOTTOM_POINT,
            self.FACE_LEFT_POINT,
            self.FACE_RIGHT_POINT,
        ):
            return None

        for hand in hands:
            hand_points = hand.get("points", {})
            for point_name in self.FINGERTIP_POINTS:
                if not self._has_point(hand_points, point_name):
                    continue

                fingertip = hand_points[point_name]
                if point_in_bounds(
                    fingertip,
                    face_data[self.FACE_TOP_POINT],
                    face_data[self.FACE_BOTTOM_POINT],
                    face_data[self.FACE_LEFT_POINT],
                    face_data[self.FACE_RIGHT_POINT],
                ):
                    return self.TOUCH_DETECTED

        return self.TOUCH_CLEAR

    def _analyze_face_touch(self, frames: list[dict[str, Any]]) -> float | None:
        touch_scores = [
            score
            for frame_data in frames
            if (score := self._score_face_touch(frame_data)) is not None
        ]
        touch_ratio = average_available(touch_scores)

        if touch_ratio is None:
            return None

        return normalize_inverse(touch_ratio, self.TOUCH_PENALTY_SCALE, self.DEFAULT_SCORE)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_score = self._analyze_head_stability(frames)
        fidget_score = self._analyze_shoulder_fidgeting(frames)
        face_touch_score = self._analyze_face_touch(frames)

        return weighted_average([
            (head_score, self.BASIC_WEIGHT) if head_score is not None else None,
            (fidget_score, self.BODY_WEIGHT) if fidget_score is not None else None,
            (face_touch_score, self.ADVANCED_WEIGHT) if face_touch_score is not None else None,
        ])
