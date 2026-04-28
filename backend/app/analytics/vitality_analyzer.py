from analytics.base_analyzer import BaseAnalyzer
from analytics.config import AnalyticsConfig
from analytics.math_utils import absolute_axis_distance, clamp_score, points_exist


class VitalityAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        score = AnalyticsConfig.VITALITY_BASE_SCORE
        hands = data.get("hands", [])
        face_data = data.get("face")

        visible_hands = min(len(hands), AnalyticsConfig.VITALITY_MAX_HANDS_COUNTED)
        score += visible_hands * AnalyticsConfig.VITALITY_HAND_BONUS

        if points_exist(face_data, "mouth_top", "mouth_bottom"):
            mouth_gap = absolute_axis_distance(
                face_data["mouth_top"],
                face_data["mouth_bottom"],
                "y",
            )
            score += mouth_gap * AnalyticsConfig.VITALITY_MOUTH_GAP_SCALE

        return clamp_score(score)
