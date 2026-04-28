from analytics.base_analyzer import BaseAnalyzer
from analytics.config import AnalyticsConfig
from analytics.math_utils import absolute_axis_distance, clamp_score, points_exist


class PresenceAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        pose_data = data.get("pose")

        if not points_exist(pose_data, "left_elbow", "right_elbow"):
            return 0.0

        elbow_distance = absolute_axis_distance(
            pose_data["left_elbow"],
            pose_data["right_elbow"],
            "x",
        )

        score = elbow_distance * AnalyticsConfig.PRESENCE_ELBOW_DISTANCE_SCALE
        return clamp_score(score)
