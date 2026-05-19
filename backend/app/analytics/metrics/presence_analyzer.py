from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    average_score,
    axis_distance,
    normalize_direct,
    normalize_inverse,
    weighted_average,
)


class PresenceAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.3
    BODY_WEIGHT = 0.5
    ADVANCED_WEIGHT = 0.2
    IDEAL_FACE_WIDTH = 0.24
    FACE_SIZE_SCALE = 350.0
    ELBOW_RATIO_SCALE = 65.0
    HAND_VISIBILITY_SCALE = 50.0
    HAND_HEIGHT_SCALE = 100.0
    HAND_VISIBILITY_WEIGHT = 0.6
    HAND_HEIGHT_WEIGHT = 0.4
    BOTTOM_OF_FRAME = 1.0
    MAX_HANDS_COUNTED = 2

    def _score_face_size(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")
        face_data = frame_data.get("face")

        if self._has_points(pose_data, "left_ear", "right_ear"):
            face_width = axis_distance(pose_data["left_ear"], pose_data["right_ear"], "x")
        elif self._has_points(face_data, "left_cheek", "right_cheek"):
            face_width = axis_distance(face_data["left_cheek"], face_data["right_cheek"], "x")
        else:
            return None

        return normalize_inverse(
            abs(face_width - self.IDEAL_FACE_WIDTH),
            self.FACE_SIZE_SCALE,
        )

    def _score_elbow_distance(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")

        if not self._has_points(
            pose_data,
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
        ):
            return None

        elbow_distance = axis_distance(
            pose_data["left_elbow"],
            pose_data["right_elbow"],
            "x",
        )
        shoulder_width = axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "x",
        )

        if shoulder_width == 0:
            return None

        return normalize_direct(elbow_distance / shoulder_width, self.ELBOW_RATIO_SCALE)

    def _score_hand_presence(self, frame_data: dict[str, Any]) -> float | None:
        hands = frame_data.get("hands", [])

        if not hands:
            return None

        visible_hands = min(len(hands), self.MAX_HANDS_COUNTED)
        visibility_score = normalize_direct(visible_hands, self.HAND_VISIBILITY_SCALE)

        hand_y_positions = [
            hand["points"]["hand_wrist"]["y"]
            for hand in hands
            if self._has_points(hand.get("points"), "hand_wrist")
        ]

        if not hand_y_positions:
            return visibility_score

        height_score = normalize_direct(
            self.BOTTOM_OF_FRAME - average(hand_y_positions),
            self.HAND_HEIGHT_SCALE,
        )
        return weighted_average([
            (visibility_score, self.HAND_VISIBILITY_WEIGHT),
            (height_score, self.HAND_HEIGHT_WEIGHT),
        ])

    def _analyze_face_size(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_face_size(frame_data)) is not None
        ]

        return average_score(scores)

    def _analyze_elbow_distance(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_elbow_distance(frame_data)) is not None
        ]

        return average_score(scores)

    def _analyze_hand_presence(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_hand_presence(frame_data)) is not None
        ]

        return average_score(scores)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        face_score = self._analyze_face_size(frames)
        elbow_score = self._analyze_elbow_distance(frames)
        hand_score = self._analyze_hand_presence(frames)

        return weighted_average([
            (face_score, self.BASIC_WEIGHT) if face_score is not None else None,
            (elbow_score, self.BODY_WEIGHT) if elbow_score is not None else None,
            (hand_score, self.ADVANCED_WEIGHT) if hand_score is not None else None,
        ])
