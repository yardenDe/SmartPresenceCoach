from analytics.base_analyzer import BaseAnalyzer
from analytics.config import AnalyticsConfig
from analytics.math_utils import absolute_axis_distance, clamp_score, points_exist


class PostureAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        pose_data = data.get("pose")

        if not points_exist(pose_data, "left_shoulder", "right_shoulder"):
            return 0.0

        shoulder_gap = absolute_axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "y",
        )

        score = AnalyticsConfig.DEFAULT_SCORE - (
            shoulder_gap * AnalyticsConfig.POSTURE_ALIGNMENT_SCALE
        )
        return clamp_score(score)
