from analytics.base_analyzer import BaseAnalyzer
from analytics.config import AnalyticsConfig
from analytics.math_utils import clamp_score, point_distance, point_exists


class ComposureAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        score = AnalyticsConfig.DEFAULT_SCORE
        face_data = data.get("face")
        hands = data.get("hands", [])

        if not point_exists(face_data, "iris_center") or not hands:
            return clamp_score(score)

        face_center = face_data["iris_center"]

        for hand in hands:
            wrist = hand.get("wrist")
            if not wrist:
                continue

            face_hand_distance = point_distance(wrist, face_center)

            if face_hand_distance < AnalyticsConfig.COMPOSURE_FACE_HAND_DISTANCE_LIMIT:
                score -= AnalyticsConfig.COMPOSURE_HAND_NEAR_FACE_PENALTY

        return clamp_score(score)
