from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    average_absolute_change,
    average_available,
    average_common_point_distance,
    average_point_motion,
    clamp_score,
    percentage_of,
    point_variance,
    weighted_average,
)


class EngagementAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.2
    BODY_WEIGHT = 0.4
    ADVANCED_WEIGHT = 0.4
    HEAD_MOTION_WEIGHT = 0.7
    HEAD_VARIANCE_WEIGHT = 0.3
    MOUTH_MOTION_WEIGHT = 0.5
    HAND_MOTION_WEIGHT = 0.5
    MAX_HEAD_MOTION = 0.11
    MAX_HEAD_VARIANCE = 0.08
    MAX_BODY_MOTION = 0.14
    MAX_MOUTH_MOTION = 0.83
    MAX_HAND_MOTION = 0.14

    BODY_POINTS = [
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist_basic",
        "right_wrist_basic",
    ]
    HAND_POINTS = ["hand_wrist", "hand_index_tip", "hand_thumb_tip"]

    def _average_hand_motion(self, frames: list[dict[str, Any]]) -> float | None:
        frame_scores = []

        for index in range(1, len(frames)):
            previous_hands = frames[index - 1].get("hands", [])
            current_hands = frames[index].get("hands", [])
            hand_scores = []

            for hand_index, current_hand in enumerate(current_hands):
                if hand_index >= len(previous_hands):
                    continue

                hand_score = average_common_point_distance(
                    previous_hands[hand_index].get("points", {}),
                    current_hand.get("points", {}),
                    self.HAND_POINTS,
                )
                if hand_score is not None:
                    hand_scores.append(hand_score)

            if hand_scores:
                frame_scores.append(average(hand_scores))

        return average_available(frame_scores)

    def _analyze_head_motion(self, frames: list[dict[str, Any]]) -> float | None:
        nose_points = self._collect_points(frames, "pose", "nose")
        nose_motion = average_point_motion(nose_points)

        if nose_motion is None:
            return None

        motion_percentage = percentage_of(nose_motion, self.MAX_HEAD_MOTION)
        variance_percentage = percentage_of(point_variance(nose_points), self.MAX_HEAD_VARIANCE)

        return weighted_average([
            (clamp_score(motion_percentage), self.HEAD_MOTION_WEIGHT),
            (clamp_score(variance_percentage), self.HEAD_VARIANCE_WEIGHT),
        ])

    def _analyze_body_motion(self, frames: list[dict[str, Any]]) -> float | None:
        body_motion = self._average_named_point_motion(frames, "pose", self.BODY_POINTS)
        if body_motion is None:
            return None

        motion_percentage = percentage_of(body_motion, self.MAX_BODY_MOTION)

        return clamp_score(motion_percentage)

    def _analyze_mouth_motion(self, frames: list[dict[str, Any]]) -> float | None:
        mouth_motion = average_absolute_change(
            self._collect_axis_distances(frames, "face", "mouth_top", "mouth_bottom", "y")
        )

        if mouth_motion is None:
            return None

        motion_percentage = percentage_of(mouth_motion, self.MAX_MOUTH_MOTION)

        return clamp_score(motion_percentage)

    def _analyze_hand_motion(self, frames: list[dict[str, Any]]) -> float | None:
        hand_motion = self._average_hand_motion(frames)

        if hand_motion is None:
            return None

        motion_percentage = percentage_of(hand_motion, self.MAX_HAND_MOTION)

        return clamp_score(motion_percentage)

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
