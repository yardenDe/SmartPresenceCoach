from typing import Any

from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, axis_distance, clamp_score, difference, normalize_direct, points_exist, weighted_average


class VitalityAnalyzer(BaseAnalyzer):
    HAND_VISIBILITY_WEIGHT = 0.35
    MOUTH_OPENING_WEIGHT = 0.35
    MOUTH_MOTION_WEIGHT = 0.3
    MAX_HANDS_COUNTED = 2
    HAND_VISIBILITY_SCALE = 50.0
    MOUTH_GAP_SCALE = 500.0
    MOTION_VARIATION_SCALE = 120.0

    def _score_hand_visibility(self, frame_data: dict[str, Any]) -> float | None:
        hands = frame_data.get("hands", [])

        if not hands:
            return None

        visible_hands = min(len(hands), self.MAX_HANDS_COUNTED)
        return normalize_direct(visible_hands, self.HAND_VISIBILITY_SCALE)

    def _score_mouth_opening(self, frame_data: dict[str, Any]) -> float | None:
        face_data = frame_data.get("face")

        if not points_exist(face_data, "mouth_top", "mouth_bottom"):
            return None

        mouth_gap = axis_distance(
            face_data["mouth_top"],
            face_data["mouth_bottom"],
            "y",
        )
        return normalize_direct(mouth_gap, self.MOUTH_GAP_SCALE)

    def _has_energy_signal(self, frame_data: dict[str, Any]) -> bool:
        return bool(
            self._score_hand_visibility(frame_data) is not None
            or self._score_mouth_opening(frame_data) is not None
        )

    def _analyze_hand_visibility(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_hand_visibility(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def _analyze_mouth_opening(self, frames: list[dict[str, Any]]) -> float | None:
        scores = [
            score
            for frame_data in frames
            if (score := self._score_mouth_opening(frame_data)) is not None
        ]

        if not scores:
            return None

        return clamp_score(average(scores))

    def _analyze_mouth_motion(self, frames: list[dict[str, Any]]) -> float | None:
        mouth_gaps = []

        for frame_data in frames:
            face_data = frame_data.get("face")
            if not points_exist(face_data, "mouth_top", "mouth_bottom"):
                continue

            mouth_gaps.append(
                axis_distance(face_data["mouth_top"], face_data["mouth_bottom"], "y")
            )

        if len(mouth_gaps) < 2:
            return None

        motion_amounts = [
            difference(mouth_gaps[index], mouth_gaps[index - 1])
            for index in range(1, len(mouth_gaps))
        ]

        return normalize_direct(average(motion_amounts), self.MOTION_VARIATION_SCALE)

    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        hand_score = self._analyze_hand_visibility(frames)
        mouth_score = self._analyze_mouth_opening(frames)
        motion_score = self._analyze_mouth_motion(frames)

        return weighted_average([
            (hand_score, self.HAND_VISIBILITY_WEIGHT) if hand_score is not None else None,
            (mouth_score, self.MOUTH_OPENING_WEIGHT) if mouth_score is not None else None,
            (motion_score, self.MOUTH_MOTION_WEIGHT) if motion_score is not None else None,
        ])
