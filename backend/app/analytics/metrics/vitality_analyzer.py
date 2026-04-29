from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, axis_distance, clamp_score, difference, points_exist


class VitalityAnalyzer(BaseAnalyzer):
    BASE_SCORE = 50.0
    HAND_BONUS = 10.0
    MAX_HANDS_COUNTED = 2
    MOUTH_GAP_SCALE = 500.0
    MOTION_VARIATION_SCALE = 120.0

    def _compute_frame_score(self, frame_data):
        score = self.BASE_SCORE
        hands = frame_data.get("hands", [])
        face_data = frame_data.get("face")

        visible_hands = min(len(hands), self.MAX_HANDS_COUNTED)
        score += visible_hands * self.HAND_BONUS

        if points_exist(face_data, "mouth_top", "mouth_bottom"):
            mouth_gap = axis_distance(
                face_data["mouth_top"],
                face_data["mouth_bottom"],
                "y",
            )
            score += mouth_gap * self.MOUTH_GAP_SCALE

        return clamp_score(score)

    def _compute_motion_bonus(self, window_data):
        mouth_gaps = []

        for frame_data in window_data:
            face_data = frame_data.get("face")
            if not points_exist(face_data, "mouth_top", "mouth_bottom"):
                continue

            mouth_gaps.append(
                axis_distance(face_data["mouth_top"], face_data["mouth_bottom"], "y")
            )

        if len(mouth_gaps) < 2:
            return 0.0

        motion_amounts = [
            difference(mouth_gaps[index], mouth_gaps[index - 1])
            for index in range(1, len(mouth_gaps))
        ]

        return average(motion_amounts) * self.MOTION_VARIATION_SCALE

    def compute(self, window_data):
        frame_scores = [self._compute_frame_score(frame_data) for frame_data in window_data]
        base_score = average(frame_scores)
        motion_bonus = self._compute_motion_bonus(window_data)

        return clamp_score(base_score + motion_bonus)

    def analyze(self, data):
        if isinstance(data, list):
            return self.compute(data)
        return self.compute([data])
