from typing import Any

from analytics.config import AnalyticsConfig
from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, clamp_score, normalize_inverse, point_distance, point_exists, variance, weighted_average


class ComposureAnalyzer(BaseAnalyzer):
    HEAD_STABILITY_WEIGHT = 0.7
    HAND_DISTANCE_WEIGHT = 0.3
    DEFAULT_SCORE = AnalyticsConfig.DEFAULT_SCORE
    HAND_NEAR_FACE_LIMIT = 0.15
    HAND_NEAR_FACE_PENALTY = 20.0
    HEAD_MOVEMENT_VARIANCE_SCALE = 500.0

    def _score_hand_distance(self, frame_data: dict[str, Any]) -> float | None:
        face_data = frame_data.get("face")
        hands = frame_data.get("hands", [])

        if not point_exists(face_data, "iris_center") or not hands:
            return None

        face_center = face_data["iris_center"]
        penalty = 0.0
        checked_hands = 0

        for hand in hands:
            wrist = hand.get("points", {}).get("hand_wrist")
            if not wrist:
                continue

            checked_hands += 1
            face_hand_distance = point_distance(wrist, face_center)
            if face_hand_distance < self.HAND_NEAR_FACE_LIMIT:
                penalty += self.HAND_NEAR_FACE_PENALTY

        if checked_hands == 0:
            return None

        return normalize_inverse(penalty, 1.0, self.DEFAULT_SCORE)

    def _analyze_head_stability(self, frames: list[dict[str, Any]]) -> float | None:
        nose_positions_x = []
        nose_positions_y = []

        for frame_data in frames:
            pose_data = frame_data.get("pose")
            if not point_exists(pose_data, "nose"):
                continue

            nose_positions_x.append(pose_data["nose"]["x"])
            nose_positions_y.append(pose_data["nose"]["y"])

        if not nose_positions_x:
            return None

        if len(nose_positions_x) == 1:
            return self.DEFAULT_SCORE

        movement_variance = variance(nose_positions_x) + variance(nose_positions_y)
        return normalize_inverse(
            movement_variance,
            self.HEAD_MOVEMENT_VARIANCE_SCALE,
            self.DEFAULT_SCORE,
        )

    def _analyze_hand_distance(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_hand_distance(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        head_score = self._analyze_head_stability(frames)
        hand_score = self._analyze_hand_distance(frames)

        return weighted_average([
            (head_score, self.HEAD_STABILITY_WEIGHT) if head_score is not None else None,
            (hand_score, self.HAND_DISTANCE_WEIGHT) if hand_score is not None else None,
        ])
