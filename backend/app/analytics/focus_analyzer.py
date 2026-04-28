from analytics.base_analyzer import BaseAnalyzer
from analytics.config import AnalyticsConfig
from analytics.math_utils import (
    absolute_axis_distance,
    clamp_score,
    midpoint,
    point_distance,
    point_exists,
    points_exist,
)


class FocusAnalyzer(BaseAnalyzer):
    def _calculate_head_focus(self, pose_data):
        if not point_exists(pose_data, "nose"):
            return AnalyticsConfig.DEFAULT_SCORE

        nose = pose_data["nose"]
        left_ear = pose_data.get("left_ear")
        right_ear = pose_data.get("right_ear")

        if left_ear and right_ear:
            left_distance = absolute_axis_distance(nose, left_ear, "x")
            right_distance = absolute_axis_distance(nose, right_ear, "x")

            if left_distance + right_distance == 0:
                return AnalyticsConfig.DEFAULT_SCORE

            head_ratio = left_distance / (right_distance + 1e-6)
            head_deviation = abs(1 - head_ratio)
        else:
            head_deviation = abs(nose["x"] - 0.5)

        score = AnalyticsConfig.DEFAULT_SCORE - (
            head_deviation * AnalyticsConfig.HEAD_DEVIATION_SCALE
        )
        return clamp_score(score)

    def _calculate_eye_focus(self, face_data):
        if not points_exist(face_data, "iris_center", "eye_left_corner", "eye_right_corner"):
            return None

        iris_center = face_data["iris_center"]
        eye_left_corner = face_data["eye_left_corner"]
        eye_right_corner = face_data["eye_right_corner"]

        eye_center = midpoint(eye_left_corner, eye_right_corner)
        eye_deviation = point_distance(iris_center, eye_center)

        score = AnalyticsConfig.DEFAULT_SCORE - (
            eye_deviation * AnalyticsConfig.EYE_DEVIATION_SCALE
        )
        return clamp_score(score)

    def analyze(self, data):
        head_score = self._calculate_head_focus(data.get("pose"))
        eye_score = self._calculate_eye_focus(data.get("face"))

        if eye_score is None:
            return head_score

        final_score = (
            eye_score * AnalyticsConfig.FOCUS_EYE_WEIGHT
            + head_score * AnalyticsConfig.FOCUS_HEAD_WEIGHT
        )
        return clamp_score(final_score)
