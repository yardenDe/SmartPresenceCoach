from typing import Any

from analytics.visual.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average_available,
    percentage_of,
    point_in_bounds,
    point_variance,
    subtract_from,
    weighted_average,
)


class ComposureAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.4
    BODY_WEIGHT = 0.3
    ADVANCED_WEIGHT = 0.3
    TOUCH_DETECTED = 1.0
    TOUCH_CLEAR = 0.0
    MAX_HEAD_VARIANCE = 0.005
    MAX_SHOULDER_MOTION = 0.002
    MAX_TOUCH_RATIO = 0.20
    
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
            return subtract_from(0.0)

        head_variance = point_variance(nose_positions)
        variance_percentage = percentage_of(head_variance, self.MAX_HEAD_VARIANCE)

        return subtract_from(variance_percentage)

    def _analyze_shoulder_fidgeting(self, frames: list[dict[str, Any]]) -> float | None:
        shoulder_motion = self._average_named_point_motion(frames, "pose", self.SHOULDER_POINTS)
        if shoulder_motion is None:
            return None

        motion_percentage = percentage_of(shoulder_motion, self.MAX_SHOULDER_MOTION)

        return subtract_from(motion_percentage)

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
        touch_values = [
            score
            for frame_data in frames
            if (score := self._score_face_touch(frame_data)) is not None
        ]
        touch_ratio = average_available(touch_values)

        if touch_ratio is None:
            return None

        touch_percentage = percentage_of(touch_ratio, self.MAX_TOUCH_RATIO)

        return subtract_from(touch_percentage)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_score = self._analyze_head_stability(frames)
        fidget_score = self._analyze_shoulder_fidgeting(frames)
        face_touch_score = self._analyze_face_touch(frames)

        return weighted_average([
            (head_score, self.BASIC_WEIGHT) if head_score is not None else None,
            (fidget_score, self.BODY_WEIGHT) if fidget_score is not None else None,
            (face_touch_score, self.ADVANCED_WEIGHT) if face_touch_score is not None else None,
        ])
