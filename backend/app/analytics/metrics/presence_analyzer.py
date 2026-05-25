from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import (
    average,
    average_score,
    axis_distance,
    clamp_score,
    percentage_of,
    subtract_from,
    weighted_average,
)


class PresenceAnalyzer(BaseAnalyzer):
    BASIC_WEIGHT = 0.3
    BODY_WEIGHT = 0.5
    ADVANCED_WEIGHT = 0.2
    IDEAL_FACE_WIDTH = 0.24
    MAX_FACE_WIDTH_DEVIATION = 0.29
    MAX_ELBOW_SHOULDER_RATIO = 1.5
    IDEAL_HAND_Y = 0.65
    MAX_HAND_Y_DEVIATION = 0.35
    CROSSED_HANDS_PENALTY = 35.0

    def _score_face_size(self, frame_data: dict[str, Any]) -> float | None:
        pose_data = frame_data.get("pose")
        face_data = frame_data.get("face")

        if self._has_points(pose_data, "left_ear", "right_ear"):
            face_width = axis_distance(pose_data["left_ear"], pose_data["right_ear"], "x")
        elif self._has_points(face_data, "left_cheek", "right_cheek"):
            face_width = axis_distance(face_data["left_cheek"], face_data["right_cheek"], "x")
        else:
            return None

        face_width_deviation = abs(face_width - self.IDEAL_FACE_WIDTH)
        deviation_percentage = percentage_of(face_width_deviation, self.MAX_FACE_WIDTH_DEVIATION)

        return subtract_from(deviation_percentage)

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

        elbow_shoulder_ratio = elbow_distance / shoulder_width
        ratio_percentage = percentage_of(elbow_shoulder_ratio, self.MAX_ELBOW_SHOULDER_RATIO)

        return clamp_score(ratio_percentage)

    def _score_hand_position(self, frame_data: dict[str, Any]) -> float | None:
        hands = frame_data.get("hands", [])

        if not hands:
            return None

        hand_y_positions = []
        wrists_by_label = {}

        for hand in hands:
            if not self._has_points(hand.get("points"), "hand_wrist"):
                continue

            wrist = hand["points"]["hand_wrist"]
            hand_y_positions.append(wrist["y"])

            if hand.get("label") in {"Left", "Right"}:
                wrists_by_label[hand["label"]] = wrist

        if not hand_y_positions:
            return None

        average_hand_y = average(hand_y_positions)
        y_deviation = abs(average_hand_y - self.IDEAL_HAND_Y)
        deviation_percentage = percentage_of(y_deviation, self.MAX_HAND_Y_DEVIATION)
        score = subtract_from(deviation_percentage)

        if (
            self._has_points(wrists_by_label, "Left", "Right")
            and wrists_by_label["Left"]["x"] > wrists_by_label["Right"]["x"]
        ):
            return subtract_from(self.CROSSED_HANDS_PENALTY, score)

        return score

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

    def _analyze_hand_position(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_hand_position(frame_data)) is not None
        ]

        return average_score(scores)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        face_score = self._analyze_face_size(frames)
        elbow_score = self._analyze_elbow_distance(frames)
        hand_score = self._analyze_hand_position(frames)

        return weighted_average([
            (face_score, self.BASIC_WEIGHT) if face_score is not None else None,
            (elbow_score, self.BODY_WEIGHT) if elbow_score is not None else None,
            (hand_score, self.ADVANCED_WEIGHT) if hand_score is not None else None,
        ])
