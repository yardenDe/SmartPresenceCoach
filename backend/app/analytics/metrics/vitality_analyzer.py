from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    average_absolute_change,
    average_available,
    average_point_motion,
    axis_distance,
    normalize_direct,
    point_distance,
    point_variance,
    weighted_average,
)


class VitalityAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.2
    BODY_WEIGHT = 0.4
    ADVANCED_WEIGHT = 0.4
    HEAD_MOTION_WEIGHT = 0.7
    HEAD_VARIANCE_WEIGHT = 0.3
    MOUTH_MOTION_WEIGHT = 0.5
    HAND_MOTION_WEIGHT = 0.5
    BODY_POINTS = [
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist_basic",
        "right_wrist_basic",
    ]
    HAND_POINTS = ["hand_wrist", "hand_index_tip", "hand_thumb_tip"]
    HEAD_MOTION_SCALE = 900.0
    HEAD_VARIANCE_SCALE = 1200.0
    BODY_MOTION_SCALE = 700.0
    MOTION_VARIATION_SCALE = 120.0
    HAND_MOTION_SCALE = 700.0

    def _collect_axis_distances(
        self,
        frames: list[dict[str, Any]],
        source: str,
        point_a_name: str,
        point_b_name: str,
        axis: str,
    ) -> list[float]:
        distances = []

        for frame in frames:
            source_data = frame.get(source)
            if self._has_points(source_data, point_a_name, point_b_name):
                distances.append(axis_distance(source_data[point_a_name], source_data[point_b_name], axis))

        return distances

    def _average_hand_motion(self, frames: list[dict[str, Any]]) -> float | None:
        frame_motions = []
        hands_by_frame = [frame.get("hands", []) for frame in frames]

        for index in range(1, len(hands_by_frame)):
            previous_hands = hands_by_frame[index - 1]
            current_hands = hands_by_frame[index]
            point_movements = []

            for hand_index, current_hand in enumerate(current_hands):
                if hand_index >= len(previous_hands):
                    continue

                previous_points = previous_hands[hand_index].get("points", {})
                current_points = current_hand.get("points", {})
                point_movements.extend([
                    point_distance(current_points[point_name], previous_points[point_name])
                    for point_name in self.HAND_POINTS
                    if self._has_points(previous_points, point_name)
                    and self._has_points(current_points, point_name)
                ])

            if point_movements:
                frame_motions.append(average(point_movements))

        return average_available(frame_motions)

    def _analyze_head_motion(self, frames: list[dict[str, Any]]) -> float | None:
        nose_points = self._collect_points(frames, "pose", "nose")
        nose_motion = average_point_motion(nose_points)

        if nose_motion is None:
            return None

        motion_score = normalize_direct(nose_motion, self.HEAD_MOTION_SCALE)
        variance_score = normalize_direct(
            point_variance(nose_points),
            self.HEAD_VARIANCE_SCALE,
        )

        return weighted_average([
            (motion_score, self.HEAD_MOTION_WEIGHT),
            (variance_score, self.HEAD_VARIANCE_WEIGHT),
        ])

    def _analyze_body_motion(self, frames: list[dict[str, Any]]) -> float | None:
        body_motion = self._average_named_point_motion(frames, "pose", self.BODY_POINTS)
        if body_motion is None:
            return None

        return normalize_direct(body_motion, self.BODY_MOTION_SCALE)

    def _analyze_hand_motion(self, frames: list[dict[str, Any]]) -> float | None:
        hand_motion = self._average_hand_motion(frames)

        if hand_motion is None:
            return None

        return normalize_direct(hand_motion, self.HAND_MOTION_SCALE)

    def _analyze_mouth_motion(self, frames: list[dict[str, Any]]) -> float | None:
        motion_amount = average_absolute_change(
            self._collect_axis_distances(frames, "face", "mouth_top", "mouth_bottom", "y")
        )

        if motion_amount is None:
            return None

        return normalize_direct(motion_amount, self.MOTION_VARIATION_SCALE)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_score = self._analyze_head_motion(frames)
        body_score = self._analyze_body_motion(frames)
        mouth_score = self._analyze_mouth_motion(frames)
        hand_score = self._analyze_hand_motion(frames)
        advanced_score = weighted_average([
            (mouth_score, self.MOUTH_MOTION_WEIGHT) if mouth_score is not None else None,
            (hand_score, self.HAND_MOTION_WEIGHT) if hand_score is not None else None,
        ])

        return weighted_average([
            (head_score, self.BASIC_WEIGHT) if head_score is not None else None,
            (body_score, self.BODY_WEIGHT) if body_score is not None else None,
            (advanced_score, self.ADVANCED_WEIGHT) if advanced_score is not None else None,
        ])
